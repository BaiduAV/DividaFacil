from fastapi import APIRouter, HTTPException, Request, Form
from pydantic import BaseModel
from src.services.database_service import DatabaseService
from src.auth import login_user, logout_user

router = APIRouter(prefix="/api", tags=["auth"])

class LoginRequest(BaseModel):
    email: str

@router.post("/login")
async def api_login(request: Request, email: str = Form(...)):
    """API login endpoint that accepts form data (for compatibility with existing tests)."""
    user = DatabaseService.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Login the user by setting session
    login_user(request, user)

    return {"message": "Login successful", "user_id": user.id, "user_name": user.name}

@router.post("/logout")
async def api_logout(request: Request):
    """API logout endpoint."""
    logout_user(request)
    return {"message": "Logout successful"}
