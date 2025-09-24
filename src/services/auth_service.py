from typing import Optional

import bcrypt

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
