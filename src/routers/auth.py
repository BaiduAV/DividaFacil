from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, validator
from typing import Optional
from src.services.user_service import UserService
from src.utils.password_validation import validate_password

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthSchema(BaseModel):
    username: str
    password: str

    @validator("password")
    def password_validator(cls, v):
        validate_password(v)
        return v

@router.post("/login")
def login(auth: AuthSchema):
    user = UserService.authenticate(auth.username, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )
    return {"message": "Login realizado com sucesso", "user_id": user.id}

@router.post("/register")
def register(auth: AuthSchema):
    # Password validation is already handled by AuthSchema
    user = UserService.create_user(auth.username, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o usuário"
        )
    return {"message": "Usuário criado com sucesso", "user_id": user.id}