from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from src.auth import login_user, logout_user
from src.services.auth_service import AuthService
from src.services.database_service import DatabaseService

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/login")
async def api_login(request: Request, login_data: LoginRequest):
    """API login endpoint that accepts JSON data with email and password authentication."""
    # Authenticate user with password
    user = AuthService.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Login the user by setting session
    login_user(request, user)

    return {"message": "Login successful", "user_id": user.id, "user_name": user.name}


@router.post("/signup")
async def api_signup(request: Request, signup_data: SignupRequest):
    """API signup endpoint for user registration."""
    # Validate password strength
    if len(signup_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    # Register user
    user = AuthService.register_user(signup_data.name, signup_data.email, signup_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Login the new user
    login_user(request, user)

    return {"message": "Registration successful", "user_id": user.id, "user_name": user.name}


@router.post("/logout")
async def api_logout(request: Request):
    """API logout endpoint."""
    logout_user(request)
    return {"message": "Logout successful"}


@router.post("/forgot-password")
async def forgot_password(forgot_data: ForgotPasswordRequest):
    """Request password reset token."""
    reset_token = AuthService.generate_reset_token(forgot_data.email)
    
    if reset_token:
        # In a real application, you would send this token via email
        # For now, we'll return it in the response (for development only)
        # TODO: Implement email sending service
        return {"message": "Password reset token generated", "token": reset_token}
    else:
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password") 
async def reset_password(reset_data: ResetPasswordRequest):
    """Reset password using reset token."""
    if len(reset_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    success = AuthService.reset_password(reset_data.token, reset_data.password)
    
    if success:
        return {"message": "Password reset successful"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
