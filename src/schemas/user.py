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
    
    @classmethod
    def from_user(cls, user):
        """Create UserResponse from User model."""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            balance=user.balance
        )
