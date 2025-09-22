import pytest
from fastapi.testclient import TestClient
from src.services.auth_service import AuthService
from src.services.database_service import DatabaseService


def test_user_registration_and_authentication():
    """Test user registration and authentication functionality."""
    # Test user registration
    user = AuthService.register_user("Test User", "test@example.com", "password123")
    assert user is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    
    # Test authentication with correct credentials
    authenticated_user = AuthService.authenticate_user("test@example.com", "password123")
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    
    # Test authentication with wrong password
    wrong_auth = AuthService.authenticate_user("test@example.com", "wrongpassword")
    assert wrong_auth is None
    
    # Test authentication with non-existent email
    no_user_auth = AuthService.authenticate_user("nonexistent@example.com", "password123")
    assert no_user_auth is None


def test_password_hashing():
    """Test password hashing functionality."""
    password = "testpassword123"
    hash1 = AuthService.hash_password(password)
    hash2 = AuthService.hash_password(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2
    
    # Both hashes should verify the same password
    assert AuthService.verify_password(password, hash1)
    assert AuthService.verify_password(password, hash2)
    
    # Wrong password should not verify
    assert not AuthService.verify_password("wrongpassword", hash1)


def test_duplicate_email_registration():
    """Test that duplicate email registration is prevented."""
    AuthService.register_user("User 1", "duplicate@example.com", "password1")
    
    # Try to register another user with the same email
    duplicate_user = AuthService.register_user("User 2", "duplicate@example.com", "password2")
    assert duplicate_user is None