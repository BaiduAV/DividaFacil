from contextlib import contextmanager
from typing import Dict, List, Optional

from src.database import create_tables, get_db
from src.models.group import Group
from src.models.user import User
from src.repositories.expense_repository import ExpenseRepository
from src.repositories.group_repository import GroupRepository
from src.repositories.user_repository import UserRepository


class DatabaseService:
    """Service to manage database operations and provide unified access to repositories."""

    @staticmethod
    def initialize():
        """Initialize database tables."""
        create_tables()

    @staticmethod
    @contextmanager
    def get_session():
        """Get a database session with automatic cleanup."""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def get_all_users() -> Dict[str, User]:
        """Get all users as a dictionary (compatible with current state interface)."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            users = user_repo.get_all()
            return {user.id: user for user in users}

    @staticmethod
    def get_all_groups() -> Dict[str, Group]:
        """Get all groups as a dictionary (compatible with current state interface)."""
        with DatabaseService.get_session() as db:
            group_repo = GroupRepository(db)
            groups = group_repo.get_all()
            return {group.id: group for group in groups}

    @staticmethod
    def create_user(name: str, email: str) -> User:
        """Create a new user."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.create(name, email)

    @staticmethod
    def create_user_with_password(name: str, email: str, password_hash: str) -> User:
        """Create a new user with password hash."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.create_with_password(name, email, password_hash)

    @staticmethod
    def create_group(name: str, member_ids: List[str] | None = None) -> Group:
        """Create a new group with optional member IDs."""
        with DatabaseService.get_session() as db:
            group_repo = GroupRepository(db)
            return group_repo.create(name, member_ids or [])

    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """Get user by ID."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.get_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.get_by_email(email)

    @staticmethod
    def get_group(group_id: str) -> Group:
        """Get group by ID."""
        with DatabaseService.get_session() as db:
            group_repo = GroupRepository(db)
            return group_repo.get_by_id(group_id)

    @staticmethod
    def add_member_to_group(group_id: str, user_id: str) -> bool:
        """Add member to group (legacy name)."""
        with DatabaseService.get_session() as db:
            group_repo = GroupRepository(db)
            return group_repo.add_member(group_id, user_id)

    @staticmethod
    def add_group_member(group_id: str, user_id: str) -> bool:
        """Add member to group (method name used by routers)."""
        return DatabaseService.add_member_to_group(group_id, user_id)

    @staticmethod
    def update_user_balances(users: Dict[str, User]):
        """Update user balances in database."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            for user in users.values():
                user_repo.update_balance(user.id, user.balance)

    @staticmethod
    def add_expense_to_group(group_id: str, expense) -> None:
        """Add expense to group."""
        with DatabaseService.get_session() as db:
            expense_repo = ExpenseRepository(db)
            expense_repo.create(expense, group_id)

    @staticmethod
    def pay_installment(expense_id: str, installment_number: int) -> bool:
        """Mark installment as paid."""
        with DatabaseService.get_session() as db:
            expense_repo = ExpenseRepository(db)
            return expense_repo.pay_installment(expense_id, installment_number)

    @staticmethod
    def update_expense(expense) -> None:
        """Update an existing expense."""
        with DatabaseService.get_session() as db:
            expense_repo = ExpenseRepository(db)
            expense_repo.update(expense)

    @staticmethod
    def delete_expense(expense_id: str) -> bool:
        """Delete an expense."""
        with DatabaseService.get_session() as db:
            expense_repo = ExpenseRepository(db)
            return expense_repo.delete(expense_id)
