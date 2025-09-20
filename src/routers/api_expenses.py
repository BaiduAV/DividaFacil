from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import uuid

from src.services.database_service import DatabaseService
from src.models.expense import Expense
from src.schemas.expense import ExpenseCreate, ExpenseResponse, InstallmentResponse
from src.services.expense_service import ExpenseService
from src.auth import require_authentication

router = APIRouter(prefix="/api", tags=["expenses"])


@router.post("/groups/{group_id}/expenses", response_model=ExpenseResponse, status_code=201)
async def create_expense_api(group_id: str, expense_data: ExpenseCreate, request: Request):
    """Create a new expense via JSON API."""
    # Require authentication
    current_user = require_authentication(request)
    
    # Validate group exists
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Validate paid_by user exists and is in group
    if expense_data.paid_by not in group.members:
        raise HTTPException(status_code=400, detail="paid_by user must be a member of the group")
    
    # Validate split_among users exist and are in group
    for user_id in expense_data.split_among:
        if user_id not in group.members:
            raise HTTPException(status_code=400, detail=f"User {user_id} in split_among must be a member of the group")
    
    # Validate split values
    if expense_data.split_type == "PERCENTAGE":
        total_pct = sum(expense_data.split_values.values())
        if abs(total_pct - 100.0) > 0.01:
            raise HTTPException(
                status_code=400, 
                detail=f"Percentages must sum to 100%. Current total: {total_pct:.2f}%"
            )
    elif expense_data.split_type == "EXACT":
        total_exact = sum(expense_data.split_values.values())
        if abs(total_exact - expense_data.amount) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Exact values sum ({total_exact:.2f}) must equal total amount ({expense_data.amount:.2f})"
            )
    
    # Use the provided date for both created_at and first_due_date if specified
    expense_date = expense_data.first_due_date or datetime.now()
    
    expense = Expense(
        id=str(uuid.uuid4()),
        amount=expense_data.amount,
        description=expense_data.description,
        paid_by=expense_data.paid_by,
        created_by=current_user.id,  # Set created_by to authenticated user
        split_among=expense_data.split_among,
        split_type=expense_data.split_type.value,
        split_values=expense_data.split_values,
        created_at=expense_date,
        installments_count=expense_data.installments_count,
        first_due_date=expense_date,
    )
    
    # Generate installments if applicable
    ExpenseService.generate_installments(expense)

    # Persist expense to database
    DatabaseService.add_expense_to_group(group_id, expense)

    # Recompute balances and save to database
    group = DatabaseService.get_group(group_id)  # Refresh from DB
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    
    return ExpenseResponse.from_expense(expense)


@router.get("/groups/{group_id}/expenses", response_model=list[ExpenseResponse])
async def list_expenses_api(group_id: str, request: Request):
    """List all expenses for a group via JSON API, filtered by authenticated user."""
    # Require authentication
    current_user = require_authentication(request)
    
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Filter expenses created by the current user, with fallback to paid_by for legacy data
    user_expenses = [
        exp for exp in group.expenses 
        if (exp.created_by == current_user.id) or 
           (exp.created_by is None and exp.paid_by == current_user.id)
    ]
    
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    
    return [ExpenseResponse.from_expense(expense) for expense in user_expenses]


@router.post("/groups/{group_id}/expenses/{expense_id}/installments/{number}/pay", status_code=204)
async def pay_installment_api(group_id: str, expense_id: str, number: int, request: Request):
    """Mark an installment as paid via JSON API."""
    # Require authentication
    require_authentication(request)
    
    if not DatabaseService.pay_installment(expense_id, number):
        raise HTTPException(status_code=404, detail="Installment not found or already paid")
    
    # Recompute balances and save to database
    group = DatabaseService.get_group(group_id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return {}


@router.delete("/groups/{group_id}/expenses/{expense_id}", status_code=204)
async def delete_expense_api(group_id: str, expense_id: str, request: Request):
    """Delete an expense via JSON API."""
    # Require authentication
    current_user = require_authentication(request)
    
    # Check if expense exists and user is the creator
    group = DatabaseService.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    expense = next((exp for exp in group.expenses if exp.id == expense_id), None)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Only allow the creator to delete the expense (or paid_by for legacy data)
    if not ((expense.created_by == current_user.id) or 
            (expense.created_by is None and expense.paid_by == current_user.id)):
        raise HTTPException(status_code=403, detail="Only the creator can delete this expense")
    
    if not DatabaseService.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Recompute balances and save to database
    group = DatabaseService.get_group(group_id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return {}
