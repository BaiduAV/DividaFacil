from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from src.template_engine import templates
from src.services.database_service import DatabaseService
from src.auth import login_user, logout_user, get_current_user_from_session

router = APIRouter(tags=["web-auth"])  # no prefix for root level forms

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    if get_current_user_from_session(request):
        return RedirectResponse("/", status_code=303)
    users = list(DatabaseService.get_all_users().values())
    return templates.TemplateResponse("login.html", {"request": request, "users": users, "current_user": None, "error": None})

@router.post("/login")
async def login_submit(request: Request, email: str = Form(...)):
    user = DatabaseService.get_user_by_email(email)
    if not user:
        users = list(DatabaseService.get_all_users().values())
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": users, "current_user": None, "error": "Usuário não encontrado"},
            status_code=400,
        )
    login_user(request, user)
    return RedirectResponse("/", status_code=303)

@router.post("/logout")
async def logout_submit(request: Request):
    if get_current_user_from_session(request):
        logout_user(request)
    return RedirectResponse("/login", status_code=303)

