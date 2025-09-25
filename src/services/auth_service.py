from typing import Optional
import secrets
import bcrypt
from datetime import datetime, timedelta

from src.models.user import User
from src.services.database_service import DatabaseService


class AuthService:
    """Service for handling user authentication."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
        return password_hash.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = DatabaseService.get_user_by_email(email)
        if not user or not user.password_hash:
            return None

        if AuthService.verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    def register_user(name: str, email: str, password: str) -> Optional[User]:
        """Register a new user with password."""
        # Check if user already exists
        existing_user = DatabaseService.get_user_by_email(email)
        if existing_user:
            return None

        # Hash the password
        password_hash = AuthService.hash_password(password)

        # Create user with password hash
        return DatabaseService.create_user_with_password(name, email, password_hash)

    @staticmethod
    def generate_reset_token(email: str) -> Optional[str]:
        """Generate a password reset token for the user."""
        user = DatabaseService.get_user_by_email(email)
        if not user:
            return None
        
        # Generate a secure random token
        reset_token = secrets.token_urlsafe(32)
        
        # Set expiry to 1 hour from now
        expiry = datetime.utcnow() + timedelta(hours=1)
        
        # Store the token in database
        if DatabaseService.update_user_reset_token(user.id, reset_token, expiry):
            return reset_token
        return None

    @staticmethod
    def reset_password(reset_token: str, new_password: str) -> bool:
        """Reset user password using a valid reset token."""
        user = DatabaseService.get_user_by_reset_token(reset_token)
        if not user:
            return False
        
        # Hash the new password
        password_hash = AuthService.hash_password(new_password)
        
        # Update password and clear reset token
        return DatabaseService.update_user_password(user.id, password_hash)
