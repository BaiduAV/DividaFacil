from pydantic import BaseModel
from typing import List, Dict

from src.models.group import Group
from .user import UserResponse


class GroupCreate(BaseModel):
    name: str
    member_ids: List[str] = []


class GroupResponse(BaseModel):
    id: str
    name: str
    members: Dict[str, UserResponse]

    class Config:
        from_attributes = True
    
    @classmethod
    def from_group(cls, group: Group) -> "GroupResponse":
        """Create GroupResponse from Group model."""
        return cls(
            id=group.id,
            name=group.name,
            members={
                user_id: UserResponse.from_user(user) 
                for user_id, user in group.members.items()
            }
        )
