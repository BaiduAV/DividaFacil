from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional

from src.database import create_tables, get_db
from src.models.group import Group
from src.models.user import User
from src.repositories.expense_repository import ExpenseRepository
from src.services.split_calculator import calculate_portions
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
    def update_user_reset_token(user_id: str, reset_token: str, expiry: datetime) -> bool:
        """Update user's password reset token and expiry."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.update_reset_token(user_id, reset_token, expiry)

    @staticmethod
    def get_user_by_reset_token(reset_token: str) -> Optional[User]:
        """Get user by reset token."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.get_by_reset_token(reset_token)

    @staticmethod
    def update_user_password(user_id: str, password_hash: str) -> bool:
        """Update user's password hash and clear reset token."""
        with DatabaseService.get_session() as db:
            user_repo = UserRepository(db)
            return user_repo.update_password(user_id, password_hash)

    @staticmethod
    def get_group(group_id: str) -> Optional[Group]:
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
    def delete_group(group_id: str) -> bool:
        """Delete group by ID."""
        with DatabaseService.get_session() as db:
            group_repo = GroupRepository(db)
            return group_repo.delete(group_id)

    @staticmethod
    def is_group_settled(group_id: str) -> bool:
        """Check if a group is settled (all balances below threshold)."""
        group = DatabaseService.get_group(group_id)
        if not group:
            return True  # Non-existent groups are considered "settled"

        from src.constants import MIN_BALANCE_THRESHOLD

        # Calculate group-specific balances (same logic as GroupResponse)
        group_balances = {user_id: {} for user_id in group.members.keys()}

        for expense in group.expenses:
            raw_portions = calculate_portions(expense)
            portions = {uid: amt for uid, amt in raw_portions.items() if uid in group.members}

            # Apply portions to balances
            for uid, owed_amount in portions.items():
                if uid == expense.paid_by:
                    continue  # Payer doesn't owe themselves

                # uid owes expense.paid_by the owed_amount
                if expense.paid_by not in group_balances[uid]:
                    group_balances[uid][expense.paid_by] = 0
                group_balances[uid][expense.paid_by] += owed_amount

                # expense.paid_by is owed by uid
                if uid not in group_balances[expense.paid_by]:
                    group_balances[expense.paid_by][uid] = 0
                group_balances[expense.paid_by][uid] -= owed_amount

        # Check pairwise balances: if any owed amount above threshold remains, not settled
        # If any pair has a non-zero outstanding amount (>= threshold) in either direction, not settled.
        member_ids = list(group.members.keys())
        for i, uid in enumerate(member_ids):
            for vid in member_ids[i + 1 :]:
                a = group_balances.get(uid, {}).get(vid, 0)
                b = group_balances.get(vid, {}).get(uid, 0)
                # Sanity: they should be opposite signs; if not, still treat as unsettled if either magnitude >= threshold
                if abs(a) >= MIN_BALANCE_THRESHOLD or abs(b) >= MIN_BALANCE_THRESHOLD:
                    # Consider them unsettled if their sum not ~0 or either magnitude significant
                    if round(a + b, 2) != 0 or abs(a) >= MIN_BALANCE_THRESHOLD or abs(b) >= MIN_BALANCE_THRESHOLD:
                        return False

        return True

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
        # Invalidate any cached settlement notion by recomputing (no cache yet, placeholder for future)

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
