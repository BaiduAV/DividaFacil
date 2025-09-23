"""Simple session-based authentication for DividaFacil."""
from typing import Optional
from fastapi import HTTPException, Request, status
from src.services.database_service import DatabaseService
from src.models.user import User


def get_current_user_from_session(request: Request) -> Optional[User]:
    """Get the current user from session. Returns None if not authenticated."""
    user_id = request.session.get("user_id")
    if user_id:
        return DatabaseService.get_user(user_id)
    return None


def require_authentication(request: Request) -> User:
    """Require authentication and return the current user. Raises HTTPException if not authenticated."""
    user = get_current_user_from_session(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user


def login_user(request: Request, user: User) -> None:
    """Log in a user by storing their ID in the session."""
    request.session["user_id"] = user.id


def logout_user(request: Request) -> None:
    """Log out the current user by clearing the session."""
    request.session.clear()