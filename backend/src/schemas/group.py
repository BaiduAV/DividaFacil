from typing import Dict, List

from pydantic import BaseModel

from src.models.group import Group

from .user import UserResponse
from .expense import ExpenseResponse


class GroupCreate(BaseModel):
    name: str
    member_ids: List[str] = []
    member_emails: List[str] = []


class GroupResponse(BaseModel):
    id: str
    name: str
    members: Dict[str, UserResponse]
    expenses: List[ExpenseResponse] = []
    balances: Dict[str, float] = {}

    class Config:
        from_attributes = True

    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        """Create GroupResponse from Group model."""
        # Calculate group-specific balances based only on expenses in this group
        balances = cls._calculate_group_specific_balances(group)

        return cls(
            id=group.id,
            name=group.name,
            members={
                user_id: UserResponse.from_user(user) for user_id, user in group.members.items()
            },
            expenses=[
                ExpenseResponse.from_expense(expense) for expense in group.expenses
            ],
            balances=balances,
        )

    @classmethod
    def _calculate_group_specific_balances(cls, group: Group) -> Dict[str, float]:
        """Calculate balances based only on expenses within this specific group."""
        # Initialize balances for all group members
        group_balances = {user_id: {} for user_id in group.members.keys()}
        
        # Process each expense in this group
        for expense in group.expenses:
            if expense.paid_by not in group.members:
                continue  # Skip if payer is not a group member
            
            # Calculate portions for this expense
            portions = {}
            if expense.split_type == "EQUAL":
                per_person = expense.amount / len(expense.split_among)
                portions = {uid: round(per_person, 2) for uid in expense.split_among if uid in group.members}
                # Handle rounding differences
                diff = round(expense.amount - sum(portions.values()), 2)
                if abs(diff) > 0.001:
                    # Add difference to last person (preferably not the payer)
                    candidates = [uid for uid in expense.split_among if uid != expense.paid_by and uid in group.members]
                    if not candidates:
                        candidates = [uid for uid in expense.split_among if uid in group.members]
                    if candidates:
                        portions[candidates[-1]] = round(portions.get(candidates[-1], 0.0) + diff, 2)
            elif expense.split_type == "EXACT":
                portions = {uid: amt for uid, amt in expense.split_values.items() if uid in group.members}
            elif expense.split_type == "PERCENTAGE":
                for uid, pct in expense.split_values.items():
                    if uid in group.members:
                        portions[uid] = round((expense.amount * pct) / 100.0, 2)
            
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
        
        # Sum up net balances for each user in this group
        net_balances = {}
        for user_id in group.members.keys():
            net_balance = sum(group_balances[user_id].values())
            net_balances[user_id] = round(net_balance, 2)
        
        return net_balances
