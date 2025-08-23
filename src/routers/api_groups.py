from fastapi import APIRouter, HTTPException

from src.services.database_service import DatabaseService
from src.schemas.group import GroupCreate, GroupResponse
from src.schemas.user import UserResponse
from src.services.expense_service import ExpenseService

router = APIRouter(prefix="/api", tags=["groups"])


@router.post("/groups", response_model=GroupResponse, status_code=201)
async def create_group_api(group_data: GroupCreate):
    """Create a new group via JSON API."""
    created = DatabaseService.create_group(group_data.name, [])
    return GroupResponse.from_group(created)


@router.get("/groups", response_model=list[GroupResponse])
async def list_groups_api():
    """List all groups via JSON API."""
    groups = DatabaseService.get_all_groups()
    
    # Recompute balances for accuracy
    for group in groups.values():
        ExpenseService.recompute_group_balances(group)
        DatabaseService.update_user_balances(group.members)
    
    return [GroupResponse.from_group(group) for group in groups.values()]


@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group_api(group_id: str):
    """Get a specific group via JSON API."""
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Recompute balances for accuracy
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    
    return GroupResponse.from_group(group)


@router.post("/groups/{group_id}/members/{user_id}", status_code=204)
async def add_member_api(group_id: str, user_id: str):
    """Add a member to a group via JSON API."""
    if not DatabaseService.get_group(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    
    if not DatabaseService.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    if not DatabaseService.add_member_to_group(group_id, user_id):
        raise HTTPException(status_code=400, detail="User is already a member")
    
    return {}
