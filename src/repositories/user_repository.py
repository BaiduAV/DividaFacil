from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import uuid

from src.database import UserDB
from src.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str) -> User:
        """Create a new user in the database."""
        user_id = str(uuid.uuid4())
        db_user = UserDB(
            id=user_id,
            name=name,
            email=email,
            balance={}
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

    def _to_domain_model(self, db_user: UserDB) -> User:
        """Convert database model to domain model."""
        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            balance=db_user.balance or {}
        )
