from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str

@router.post("/login")
def login(auth: AuthSchema):
    user = AuthService.authenticate_user(auth.email, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )
    return {"message": "Login realizado com sucesso", "user_id": user.id}

@router.post("/register")
def register(auth: RegisterSchema):
    user = AuthService.register_user(auth.name, auth.email, auth.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o usuário"
        )
    return {"message": "Usuário criado com sucesso", "user_id": user.id}