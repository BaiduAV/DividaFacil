from fastapi import Request, Response
from typing import Optional
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SessionManager:
    """Enhanced session management for user authentication with production-ready features."""
    
    # In-memory session store with session expiration tracking
    # TODO: In production, replace with Redis or database for scalability and persistence
    _sessions = {}
    _session_expiry = {}  # Track session expiration times
    
    # Configuration
    SESSION_DURATION = int(os.getenv("SESSION_DURATION_DAYS", "7")) * 24 * 60 * 60  # Default 7 days in seconds
    SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"  # Enable in production with HTTPS
    
    @staticmethod
    def create_session(response: Response, user_id: str) -> str:
        """Create a new session for a user with expiration tracking."""
        import secrets
        session_id = secrets.token_urlsafe(32)
        
        # Set session data and expiration
        SessionManager._sessions[session_id] = user_id
        SessionManager._session_expiry[session_id] = datetime.utcnow() + timedelta(seconds=SessionManager.SESSION_DURATION)
        
        logger.info(f"Created session for user {user_id[:8]}...")  # Log partial user ID for security
        logger.debug(f"Total active sessions: {len(SessionManager._sessions)}")
        
        # Set secure session cookie with environment-aware security settings
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=SessionManager.SESSION_DURATION,
            httponly=True,
            secure=SessionManager.SECURE_COOKIES,  # Configurable based on environment
            samesite="lax"
        )
        return session_id
    
    @staticmethod
    def get_user_id(request: Request) -> Optional[str]:
        """Get user ID from session with automatic cleanup of expired sessions."""
        session_id = request.cookies.get("session_id")
        
        if not session_id:
            logger.debug("No session_id cookie found")
            return None
        
        # Check if session exists and is not expired
        if session_id not in SessionManager._sessions:
            logger.debug("Session not found in active sessions")
            return None
            
        # Check session expiration
        if session_id in SessionManager._session_expiry:
            if datetime.utcnow() > SessionManager._session_expiry[session_id]:
                logger.info("Session expired, cleaning up")
                SessionManager._cleanup_session(session_id)
                return None
        
        user_id = SessionManager._sessions.get(session_id)
        logger.debug("Valid session found")
        return user_id
    
    @staticmethod
    def destroy_session(request: Request, response: Response) -> bool:
        """Destroy a session and clean up all related data."""
        session_id = request.cookies.get("session_id")
        if session_id and session_id in SessionManager._sessions:
            SessionManager._cleanup_session(session_id)
            response.delete_cookie("session_id")
            logger.info("User session destroyed")
            return True
        return False
    
    @staticmethod
    def _cleanup_session(session_id: str) -> None:
        """Internal method to clean up session data."""
        if session_id in SessionManager._sessions:
            del SessionManager._sessions[session_id]
        if session_id in SessionManager._session_expiry:
            del SessionManager._session_expiry[session_id]
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """Clean up all expired sessions. Returns number of sessions cleaned up."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, expiry_time in SessionManager._session_expiry.items():
            if current_time > expiry_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            SessionManager._cleanup_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    @staticmethod
    def get_session_info() -> dict:
        """Get session statistics for monitoring (production-safe)."""
        SessionManager.cleanup_expired_sessions()  # Clean up before reporting
        return {
            "active_sessions": len(SessionManager._sessions),
            "session_duration_days": SessionManager.SESSION_DURATION // (24 * 60 * 60),
            "secure_cookies_enabled": SessionManager.SECURE_COOKIES
        }
    
    @staticmethod
    def is_authenticated(request: Request) -> bool:
        """Check if user is authenticated."""
        return SessionManager.get_user_id(request) is not None