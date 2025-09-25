from typing import Dict, List

from pydantic import BaseModel

from src.models.group import Group

from .user import UserResponse


class GroupCreate(BaseModel):
    name: str
    member_ids: List[str] = []
    member_emails: List[str] = []


class GroupResponse(BaseModel):
    id: str
    name: str
    members: Dict[str, UserResponse]
    balances: Dict[str, float] = {}

    class Config:
        from_attributes = True

    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        """Create GroupResponse from Group model."""
        # Calculate balances for the group
        balances = {}
        for user_id, user in group.members.items():
            # Sum all balance entries for this user
            total_balance = sum(user.balance.values())
            balances[user_id] = round(float(total_balance), 2)

        return cls(
            id=group.id,
            name=group.name,
            members={
                user_id: UserResponse.from_user(user) for user_id, user in group.members.items()
            },
            balances=balances,
        )
