from fastapi import APIRouter, HTTPException
import uuid

from src.services.database_service import DatabaseService
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse
from src.schemas.error import ErrorResponse

router = APIRouter(prefix="/api", tags=["users"])


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user_api(user_data: UserCreate):
    """Create a new user via JSON API."""
    # Check if user already exists
    existing_user = DatabaseService.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user via repository (generates ID)
    created = DatabaseService.create_user(user_data.name, user_data.email)
    return UserResponse.from_user(created)


@router.get("/users", response_model=list[UserResponse])
async def list_users_api():
    """List all users via JSON API."""
    users = DatabaseService.get_all_users()
    return [UserResponse.from_user(user) for user in users.values()]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_api(user_id: str):
    """Get a specific user via JSON API."""
    user = DatabaseService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_user(user)
