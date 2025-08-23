from pydantic import BaseModel, EmailStr
from typing import Dict


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    balance: Dict[str, float]

    class Config:
        from_attributes = True
