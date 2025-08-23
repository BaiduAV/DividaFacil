from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .user import User
from .expense import Expense

@dataclass
class Group:
    """Represents a group of users sharing expenses."""
    id: str
    name: str
    members: Dict[str, User] = field(default_factory=dict)  # user_id -> User
    expenses: List[Expense] = field(default_factory=list)

    def add_member(self, user: User) -> None:
        """Add a user to the group."""
        if user.id not in self.members:
            self.members[user.id] = user
            
    def remove_member(self, user_id: str) -> None:
        """Remove a user from the group."""
        if user_id in self.members:
            # TODO: Handle any outstanding balances
            del self.members[user_id]
            
    def add_expense(self, expense: Expense) -> None:
        """Add an expense to the group."""
        if expense.paid_by not in self.members:
            raise ValueError("Payer is not a member of the group")
            
        for user_id in expense.split_among:
            if user_id not in self.members:
                raise ValueError(f"User {user_id} in split is not a member of the group")
                
        expense.validate_split()
        self.expenses.append(expense)
        
    def get_expenses_for_user(self, user_id: str) -> List[Expense]:
        """Get all expenses involving a specific user."""
        return [exp for exp in self.expenses 
                if exp.paid_by == user_id or user_id in exp.split_among]
