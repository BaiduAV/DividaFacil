from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
import uuid

from src.database import GroupDB, UserDB, group_members
from src.models.group import Group
from src.models.user import User


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, member_ids: List[str] = None) -> Group:
        """Create a new group in the database."""
        group_id = str(uuid.uuid4())
        db_group = GroupDB(
            id=group_id,
            name=name
        )
        self.db.add(db_group)
        
        # Add members if provided
        if member_ids:
            members = self.db.query(UserDB).filter(UserDB.id.in_(member_ids)).all()
            db_group.members.extend(members)
        
        self.db.commit()
        self.db.refresh(db_group)
        return self._to_domain_model(db_group)

    def get_by_id(self, group_id: str) -> Optional[Group]:
        """Get group by ID with all relationships loaded."""
        db_group = self.db.query(GroupDB).options(
            selectinload(GroupDB.members),
            selectinload(GroupDB.expenses)
        ).filter(GroupDB.id == group_id).first()
        return self._to_domain_model(db_group) if db_group else None

    def get_all(self) -> List[Group]:
        """Get all groups with relationships loaded."""
        db_groups = self.db.query(GroupDB).options(
            selectinload(GroupDB.members),
            selectinload(GroupDB.expenses)
        ).all()
        return [self._to_domain_model(db_group) for db_group in db_groups]

    def add_member(self, group_id: str, user_id: str) -> bool:
        """Add a member to a group."""
        db_group = self.db.query(GroupDB).filter(GroupDB.id == group_id).first()
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        
        if db_group and db_user and db_user not in db_group.members:
            db_group.members.append(db_user)
            self.db.commit()
            return True
        return False

    def delete(self, group_id: str) -> bool:
        """Delete group by ID."""
        db_group = self.db.query(GroupDB).filter(GroupDB.id == group_id).first()
        if db_group:
            self.db.delete(db_group)
            self.db.commit()
            return True
        return False

    def _to_domain_model(self, db_group: GroupDB) -> Group:
        """Convert database model to domain model."""
        from src.repositories.expense_repository import ExpenseRepository
        
        # Convert members
        members = {
            user.id: User(id=user.id, name=user.name, email=user.email, balance=user.balance or {})
            for user in db_group.members
        }
        
        # Create group
        group = Group(id=db_group.id, name=db_group.name)
        group.members = members
        
        # Convert expenses
        expense_repo = ExpenseRepository(self.db)
        for db_expense in db_group.expenses:
            expense = expense_repo._to_domain_model(db_expense)
            group.expenses.append(expense)
        
        return group
