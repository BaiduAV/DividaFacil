from fastapi import APIRouter, HTTPException, Depends
import uuid

from src.services.database_service import DatabaseService
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse
from src.schemas.error import ErrorResponse
from src.auth import get_current_user, require_current_user_id

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
async def list_users_api(current_user_id: str = Depends(require_current_user_id)):
    """List all users via JSON API. Returns only the current user for privacy."""
    # For privacy, only return the current user's data
    user = DatabaseService.get_user(current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    return [UserResponse.from_user(user)]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_api(user_id: str, current_user_id: str = Depends(require_current_user_id)):
    """Get a specific user via JSON API. Users can only access their own data."""
    # Users can only access their own user data
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own user data.")
    
    user = DatabaseService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_user(user)
