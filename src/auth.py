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
    request.session.clear()"""
Basic authentication system for DividaFacil.
Uses simple session-based authentication with cookies.
"""
import uuid
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Cookie, Depends
from starlette.responses import Response

from src.services.database_service import DatabaseService
from src.models.user import User

# In-memory session store for simplicity
# In production, this should be Redis, database, or other persistent store
_sessions: Dict[str, str] = {}  # session_id -> user_id


def create_session(user_id: str) -> str:
    """Create a new session for a user."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = user_id
    return session_id


def get_session_user_id(session_id: str) -> Optional[str]:
    """Get user ID from session."""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> None:
    """Delete a session."""
    _sessions.pop(session_id, None)


def clear_all_sessions() -> None:
    """Clear all sessions (for testing)."""
    _sessions.clear()


def get_current_user_id(
    session_id: Optional[str] = Cookie(None, alias="session_id")
) -> Optional[str]:
    """Get current user ID from session cookie (optional)."""
    if not session_id:
        return None
    return get_session_user_id(session_id)


def get_current_user(
    session_id: Optional[str] = Cookie(None, alias="session_id")
) -> Optional[User]:
    """Get current user from session cookie (optional)."""
    user_id = get_current_user_id(session_id)
    if not user_id:
        return None
    return DatabaseService.get_user(user_id)


def require_current_user(
    session_id: Optional[str] = Cookie(None, alias="session_id")
) -> User:
    """Require authentication and return current user."""
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in first."
        )
    return user


def require_current_user_id(
    session_id: Optional[str] = Cookie(None, alias="session_id")
) -> str:
    """Require authentication and return current user ID."""
    user_id = get_current_user_id(session_id)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in first."
        )
    return user_id


def set_session_cookie(response: Response, session_id: str) -> None:
    """Set session cookie on response."""
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400 * 7  # 7 days
    )


def clear_session_cookie(response: Response) -> None:
    """Clear session cookie."""
    response.delete_cookie(key="session_id")