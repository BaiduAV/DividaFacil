import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.database import UserDB
from src.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str) -> User:
        """Create a new user in the database."""
        user_id = str(uuid.uuid4())
        default_prefs = {"email_overdue": True, "email_upcoming": True, "days_ahead_reminder": 3}
        db_user = UserDB(
            id=user_id, name=name, email=email, balance={}, notification_preferences=default_prefs
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_domain_model(db_user)

    def create_with_password(self, name: str, email: str, password_hash: str) -> User:
        """Create a new user with password hash in the database."""
        user_id = str(uuid.uuid4())
        default_prefs = {"email_overdue": True, "email_upcoming": True, "days_ahead_reminder": 3}
        db_user = UserDB(
            id=user_id,
            name=name,
            email=email,
            password_hash=password_hash,
            balance={},
            notification_preferences=default_prefs,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_domain_model(db_user)

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        return self._to_domain_model(db_user) if db_user else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db_user = self.db.query(UserDB).filter(UserDB.email == email).first()
        return self._to_domain_model(db_user) if db_user else None

    def get_all(self) -> List[User]:
        """Get all users."""
        db_users = self.db.query(UserDB).all()
        return [self._to_domain_model(db_user) for db_user in db_users]

    def update_balance(self, user_id: str, balance: Dict[str, float]):
        """Update user balance."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db_user.balance = balance
            self.db.commit()

    def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def update_notification_preferences(self, user_id: str, preferences: Dict[str, any]):
        """Update user notification preferences."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db_user.notification_preferences = preferences
            self.db.commit()
            return True
        return False

    def update_reset_token(self, user_id: str, reset_token: str, expiry: datetime) -> bool:
        """Update user's password reset token and expiry."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db_user.reset_token = reset_token
            db_user.reset_token_expiry = expiry
            self.db.commit()
            return True
        return False

    def get_by_reset_token(self, reset_token: str) -> Optional[User]:
        """Get user by reset token if token is valid."""
        db_user = self.db.query(UserDB).filter(
            UserDB.reset_token == reset_token,
            UserDB.reset_token_expiry > datetime.utcnow()
        ).first()
        return self._to_domain_model(db_user) if db_user else None

    def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user's password hash and clear reset token."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db_user.password_hash = password_hash
            db_user.reset_token = None
            db_user.reset_token_expiry = None
            self.db.commit()
            return True
        return False

    def _to_domain_model(self, db_user: UserDB) -> User:
        """Convert database model to domain model."""
        default_prefs = {"email_overdue": True, "email_upcoming": True, "days_ahead_reminder": 3}
        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            balance=db_user.balance or {},
            notification_preferences=db_user.notification_preferences or default_prefs,
            password_hash=db_user.password_hash,
            reset_token=db_user.reset_token,
            reset_token_expiry=db_user.reset_token_expiry,
        )
