import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock
from src.services.session_manager import SessionManager


def test_session_creation_with_expiration():
    """Test session creation includes expiration tracking."""
    # Clear any existing sessions
    SessionManager._sessions.clear()
    SessionManager._session_expiry.clear()
    
    # Mock response object
    response = Mock()
    user_id = "test-user-123"
    
    # Create session
    session_id = SessionManager.create_session(response, user_id)
    
    # Verify session exists
    assert session_id in SessionManager._sessions
    assert SessionManager._sessions[session_id] == user_id
    
    # Verify expiration is set
    assert session_id in SessionManager._session_expiry
    assert isinstance(SessionManager._session_expiry[session_id], datetime)
    
    # Verify expiration is in the future
    assert SessionManager._session_expiry[session_id] > datetime.utcnow()


def test_session_expiration_cleanup():
    """Test automatic cleanup of expired sessions."""
    # Clear any existing sessions
    SessionManager._sessions.clear()
    SessionManager._session_expiry.clear()
    
    # Create an expired session
    expired_session_id = "expired-session"
    SessionManager._sessions[expired_session_id] = "test-user"
    SessionManager._session_expiry[expired_session_id] = datetime.utcnow() - timedelta(hours=1)
    
    # Create a valid session
    valid_session_id = "valid-session"
    SessionManager._sessions[valid_session_id] = "test-user-2"
    SessionManager._session_expiry[valid_session_id] = datetime.utcnow() + timedelta(hours=1)
    
    # Mock request with expired session
    request_expired = Mock()
    request_expired.cookies = {"session_id": expired_session_id}
    
    # Try to get user ID - should return None and clean up expired session
    user_id = SessionManager.get_user_id(request_expired)
    assert user_id is None
    assert expired_session_id not in SessionManager._sessions
    assert expired_session_id not in SessionManager._session_expiry
    
    # Valid session should still exist
    assert valid_session_id in SessionManager._sessions
    assert valid_session_id in SessionManager._session_expiry


def test_cleanup_expired_sessions():
    """Test bulk cleanup of expired sessions."""
    # Clear any existing sessions
    SessionManager._sessions.clear()
    SessionManager._session_expiry.clear()
    
    # Create multiple expired sessions
    for i in range(3):
        session_id = f"expired-{i}"
        SessionManager._sessions[session_id] = f"user-{i}"
        SessionManager._session_expiry[session_id] = datetime.utcnow() - timedelta(hours=1)
    
    # Create valid sessions
    for i in range(2):
        session_id = f"valid-{i}"
        SessionManager._sessions[session_id] = f"user-valid-{i}"
        SessionManager._session_expiry[session_id] = datetime.utcnow() + timedelta(hours=1)
    
    # Should have 5 sessions total
    assert len(SessionManager._sessions) == 5
    assert len(SessionManager._session_expiry) == 5
    
    # Clean up expired sessions
    cleaned_count = SessionManager.cleanup_expired_sessions()
    
    # Should have cleaned up 3 sessions
    assert cleaned_count == 3
    assert len(SessionManager._sessions) == 2
    assert len(SessionManager._session_expiry) == 2
    
    # Only valid sessions should remain
    for session_id in SessionManager._sessions:
        assert session_id.startswith("valid-")


def test_session_info():
    """Test session information retrieval."""
    # Clear any existing sessions
    SessionManager._sessions.clear()
    SessionManager._session_expiry.clear()
    
    # Create some sessions
    response = Mock()
    SessionManager.create_session(response, "user1")
    SessionManager.create_session(response, "user2")
    
    # Get session info
    info = SessionManager.get_session_info()
    
    # Verify info structure
    assert "active_sessions" in info
    assert "session_duration_days" in info
    assert "secure_cookies_enabled" in info
    
    # Verify values
    assert info["active_sessions"] == 2
    assert isinstance(info["session_duration_days"], int)
    assert isinstance(info["secure_cookies_enabled"], bool)


def test_environment_configuration():
    """Test that environment variables are properly read."""
    # Test default values
    assert SessionManager.SESSION_DURATION == 7 * 24 * 60 * 60  # 7 days default
    assert SessionManager.SECURE_COOKIES == False  # Default false
    
    # Test session duration calculation
    duration_days = SessionManager.SESSION_DURATION // (24 * 60 * 60)
    assert duration_days == 7