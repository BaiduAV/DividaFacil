from datetime import datetime
from typing import Dict, Optional
import uuid

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.state import USERS
from src.models.expense import Expense
from src.services.expense_service import ExpenseService
from src.services.database_service import DatabaseService
from src.template_engine import templates
from .common import get_group_or_404

router = APIRouter()


@router.post("/groups/{group_id}/expenses")
async def add_expense(
    group_id: str,
    description: str = Form(...),
    amount: float = Form(...),
    paid_by: str = Form(...),
    split_type: str = Form(...),
    installments_count: int = Form(1),
    first_due_date: Optional[str] = Form(None),
    request: Request = None,
):
    group = get_group_or_404(group_id)
    if paid_by not in group.members:
        raise HTTPException(status_code=400, detail="Quem pagou deve ser um membro do grupo")

    form = await request.form()
    split_among = form.getlist("split_among") or list(group.members.keys())

    split_values: Dict[str, float] = {}
    if split_type in ("EXACT", "PERCENTAGE"):
        for uid in split_among:
            key = f"value_{uid}"
            if key in form and form[key] != "":
                try:
                    split_values[uid] = float(str(form[key]).replace(',', '.'))
                except ValueError:
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
                            "error": f"Número inválido para o usuário {uid}",
                        },
                        status_code=400,
                    )
        if split_type == "PERCENTAGE":
            total_pct = sum(split_values.values())
            if abs(total_pct - 100.0) > 0.01:
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
                        "error": f"Os percentuais devem somar 100%. Total atual: {total_pct:.2f}%",
                    },
                    status_code=400,
                )
        elif split_type == "EXACT":
            total_exact = round(sum(split_values.values()), 2)
            if abs(total_exact - round(amount, 2)) > 0.01:
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
                        "error": f"A soma dos valores EXATOS ({total_exact:.2f}) deve ser igual ao total ({round(amount,2):.2f})",
                    },
                    status_code=400,
                )

    # Use the provided date for both created_at and first_due_date if specified
    expense_date = datetime.fromisoformat(first_due_date) if first_due_date else datetime.now()
    
    expense = Expense(
        id=str(uuid.uuid4()),
        amount=amount,
        description=description,
        paid_by=paid_by,
        split_among=split_among,
        split_type=split_type,
        split_values=split_values if split_type in ("EXACT", "PERCENTAGE") else {},
        created_at=expense_date,
        installments_count=installments_count,
        first_due_date=expense_date,
    )

    ExpenseService.generate_installments(expense)
    DatabaseService.add_expense_to_group(group_id, expense)
    group = DatabaseService.get_group(group_id)  # Refresh from DB
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)

    return RedirectResponse(f"/groups/{group_id}", status_code=303)


@router.post("/groups/{group_id}/expenses/{expense_id}/installments/{number}/pay")
async def pay_installment(group_id: str, expense_id: str, number: int):
    if not DatabaseService.pay_installment(expense_id, number):
        raise HTTPException(status_code=404, detail="Parcela não encontrada ou já paga")
    
    # Recompute balances and save to database
    group = DatabaseService.get_group(group_id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return RedirectResponse(f"/groups/{group_id}", status_code=303)


@router.post("/groups/{group_id}/expenses/{expense_id}/edit")
async def edit_expense(
    request: Request,
    group_id: str,
    expense_id: str,
    description: str = Form(...),
    paid_by: str = Form(...),
    amount: float = Form(...),
    split_type: str = Form(...),
):
    group = get_group_or_404(group_id)
    exp = next((e for e in group.expenses if e.id == expense_id), None)
    if not exp:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    if paid_by not in group.members:
        raise HTTPException(status_code=400, detail="Quem pagou deve ser um membro do grupo")

    form = await request.form()
    split_values: Dict[str, float] = {}
    if split_type in ("EXACT", "PERCENTAGE"):
        for uid in exp.split_among:
            key = f"split_values[{uid}]"
            if key in form and form.get(key) not in (None, ""):
                try:
                    split_values[uid] = float(str(form.get(key)).replace(',', '.'))
                except ValueError:
                    return RedirectResponse(
                        f"/groups/{group_id}?error=Valor%20inv%C3%A1lido%20para%20{group.members[uid].name}",
                        status_code=303,
                    )

        if split_type == "EXACT":
            total = round(sum(split_values.values()), 2)
            if abs(total - round(amount, 2)) > 0.01:
                return RedirectResponse(
                    f"/groups/{group_id}?error=Soma%20dos%20EXACT%20({total})%20difere%20do%20total%20({round(amount,2)})",
                    status_code=303,
                )
        elif split_type == "PERCENTAGE":
            pct = round(sum(split_values.values()), 2)
            if abs(pct - 100.0) > 0.01:
                return RedirectResponse(
                    f"/groups/{group_id}?error=Soma%20dos%20percentuais%20({pct}%%)%20deve%20ser%20100%%",
                    status_code=303,
                )
    else:
        split_values = {}

    exp.description = description
    exp.paid_by = paid_by
    exp.amount = round(amount, 2)
    exp.split_type = split_type
    exp.split_values = split_values

    if exp.installments_count and exp.installments_count > 1:
        ExpenseService.generate_installments(exp)

    DatabaseService.update_expense(exp)
    
    group = DatabaseService.get_group(group_id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return RedirectResponse(f"/groups/{group_id}?success=Despesa%20atualizada", status_code=303)


@router.post("/groups/{group_id}/expenses/{expense_id}/date")
async def update_expense_date(
    group_id: str,
    expense_id: str,
    date: str = Form(...),
):
    group = DatabaseService.get_group(group_id)
    exp = next((e for e in group.expenses if e.id == expense_id), None)
    if not exp:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    try:
        new_dt = datetime.fromisoformat(date)
    except Exception:
        return RedirectResponse(f"/groups/{group_id}?error=Data%20inv%C3%A1lida", status_code=303)
    exp.created_at = new_dt
    if exp.installments_count and exp.installments_count > 1:
        exp.first_due_date = new_dt
        ExpenseService.generate_installments(exp)
    
    # Update in database
    DatabaseService.update_expense(exp)
    
    # Recompute balances and save to database
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return RedirectResponse(f"/groups/{group_id}?success=Data%20atualizada", status_code=303)


@router.post("/groups/{group_id}/expenses/{expense_id}/delete")
async def delete_expense(group_id: str, expense_id: str):
    if not DatabaseService.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    
    # Recompute balances and save to database
    group = DatabaseService.get_group(group_id)
    ExpenseService.recompute_group_balances(group)
    DatabaseService.update_user_balances(group.members)
    return RedirectResponse(f"/groups/{group_id}?success=Despesa%20exclu%C3%ADda", status_code=303)
