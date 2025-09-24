from fastapi import APIRouter, Depends, HTTPException

from src.auth import require_authentication
from src.models.user import User
from src.schemas.group import GroupCreate, GroupResponse
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService

router = APIRouter(prefix="/api", tags=["groups"])


@router.post("/groups", response_model=GroupResponse, status_code=201)
async def create_group_api(
    group_data: GroupCreate, current_user: User = Depends(require_authentication)
):
    """Create a new group via JSON API. Current user automatically becomes a member."""
    # Create group and add current user as a member
    created = DatabaseService.create_group(group_data.name, [current_user.id])
    return GroupResponse.from_group(created)


@router.get("/groups", response_model=list[GroupResponse])
async def list_groups_api(current_user: User = Depends(require_authentication)):
    """List groups where the current user is a member."""
    all_groups = DatabaseService.get_all_groups()

    # Filter to only groups where current user is a member
    user_groups = [group for group in all_groups.values() if current_user.id in group.members]

    # Recompute balances for user's groups only
    for group in user_groups:
        ExpenseService.recompute_group_balances(group)
        DatabaseService.update_user_balances(group.members)

    return [GroupResponse.from_group(group) for group in user_groups]


@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group_api(group_id: str, current_user: User = Depends(require_authentication)):
    """Get a specific group via JSON API. User must be a member."""
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if user is a member of the group
    if current_user.id not in group.members:
        raise HTTPException(
            status_code=403, detail="Access denied. You are not a member of this group."
        )

    # Recompute balances for accuracy
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)

    return GroupResponse.from_group(group)


@router.post("/groups/{group_id}/members/{user_id}", status_code=204)
async def add_member_api(
    group_id: str, user_id: str, current_user: User = Depends(require_authentication)
):
    """Add a member to a group via JSON API. User must be a member of the group."""
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if current user is a member of the group (only members can add others)
    if current_user.id not in group.members:
        raise HTTPException(
            status_code=403, detail="Access denied. You are not a member of this group."
        )

    if not DatabaseService.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    if not DatabaseService.add_member_to_group(group_id, user_id):
        raise HTTPException(status_code=400, detail="User is already a member")

    return {}
