"""
Authentication routes for login/logout functionality.
"""
from typing import Optional
from fastapi import APIRouter, Form, HTTPException, Cookie
from fastapi.responses import RedirectResponse, JSONResponse

from src.services.database_service import DatabaseService
from src.auth import create_session, delete_session, set_session_cookie, clear_session_cookie

router = APIRouter()


@router.post("/login")
async def login(email: str = Form(...)):
    """
    Simple login by email (no password for simplicity).
    In production, this should verify password.
    """
    user = DatabaseService.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Create session
    session_id = create_session(user.id)
    
    # Redirect to dashboard with session cookie
    response = RedirectResponse("/", status_code=303)
    set_session_cookie(response, session_id)
    return response


@router.post("/logout")
async def logout(session_id: Optional[str] = Cookie(None, alias="session_id")):
    """Logout and clear session."""
    if session_id:
        delete_session(session_id)
    
    response = RedirectResponse("/", status_code=303)
    clear_session_cookie(response)
    return response


# API versions for programmatic access
@router.post("/api/login")
async def login_api(email: str = Form(...)):
    """
    API login by email.
    Returns session info for setting cookie manually.
    """
    user = DatabaseService.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Create session
    session_id = create_session(user.id)
    
    response = JSONResponse({
        "message": "Login successful",
        "user_id": user.id,
        "user_name": user.name
    })
    set_session_cookie(response, session_id)
    return response


@router.post("/api/logout")
async def logout_api(session_id: Optional[str] = Cookie(None, alias="session_id")):
    """API logout."""
    if session_id:
        delete_session(session_id)
    
    response = JSONResponse({"message": "Logout successful"})
    clear_session_cookie(response)
    return response