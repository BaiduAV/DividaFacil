from fastapi import Request, Response
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Simple session management for user authentication."""
    
    # In-memory session store (in production, use Redis or database)
    _sessions = {}
    
    @staticmethod
    def create_session(response: Response, user_id: str) -> str:
        """Create a new session for a user."""
        import secrets
        session_id = secrets.token_urlsafe(32)
        SessionManager._sessions[session_id] = user_id
        
        logger.info(f"Created session {session_id} for user {user_id}")
        logger.info(f"Total sessions: {len(SessionManager._sessions)}")
        
        # Set secure session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=86400 * 7,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        return session_id
    
    @staticmethod
    def get_user_id(request: Request) -> Optional[str]:
        """Get user ID from session."""
        session_id = request.cookies.get("session_id")
        logger.info(f"Looking up session: {session_id}")
        logger.info(f"Available sessions: {list(SessionManager._sessions.keys())}")
        
        if not session_id:
            logger.info("No session_id cookie found")
            return None
        
        user_id = SessionManager._sessions.get(session_id)
        logger.info(f"Session {session_id} -> User {user_id}")
        return user_id
    
    @staticmethod
    def destroy_session(request: Request, response: Response) -> bool:
        """Destroy a session."""
        session_id = request.cookies.get("session_id")
        if session_id and session_id in SessionManager._sessions:
            del SessionManager._sessions[session_id]
            response.delete_cookie("session_id")
            logger.info(f"Destroyed session {session_id}")
            return True
        return False
    
    @staticmethod
    def is_authenticated(request: Request) -> bool:
        """Check if user is authenticated."""
        return SessionManager.get_user_id(request) is not None