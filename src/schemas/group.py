from pydantic import BaseModel
from typing import List, Dict
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
