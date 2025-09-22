from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from src.state import USERS
from src.services.database_service import DatabaseService
from src.services.expense_service import ExpenseService
from src.services.session_manager import SessionManager
from src.template_engine import templates
from .common import get_group_or_404

router = APIRouter()


@router.post("/groups")
async def create_group(request: Request, name: str = Form(...)):
    # Check if user is authenticated
    user_id = SessionManager.get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    # Safely handle single or multiple checkboxes
    form = await request.form()
    member_ids = form.getlist("member_ids")
    
    # Ensure the current user is included in the group
    if user_id not in member_ids:
        member_ids.append(user_id)
    
    group = DatabaseService.create_group(name, member_ids)
    return RedirectResponse(f"/groups/{group.id}", status_code=303)


@router.get("/groups/{group_id}", response_class=HTMLResponse)
async def group_detail(request: Request, group_id: str):
    group = get_group_or_404(group_id)
    ExpenseService.recompute_group_balances(group)
    transactions = ExpenseService.simplify_balances(group.members)
    monthly = ExpenseService.compute_monthly_analysis(group)
    monthly_transactions = ExpenseService.compute_monthly_transactions(monthly)
    expense_remaining = {e.id: ExpenseService.compute_expense_remaining(e, group) for e in group.expenses}
    return templates.TemplateResponse(
        "group_detail.html",
        {
            "request": request,
            "group": group,
            "all_users": list(USERS.values()),
            "transactions": transactions,
            "monthly": monthly,
            "monthly_transactions": monthly_transactions,
            "expense_remaining": expense_remaining,
            "error": request.query_params.get("error"),
            "success": request.query_params.get("success"),
        },
    )


@router.post("/groups/{group_id}/members")
async def add_member(group_id: str, user_id: str = Form(...)):
    if not DatabaseService.get_user(user_id):
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    DatabaseService.add_group_member(group_id, user_id)
    return RedirectResponse(f"/groups/{group_id}?success=Membro%20adicionado", status_code=303)
