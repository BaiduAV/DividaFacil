from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict, List, Optional, Union
import uuid
from datetime import datetime
import logging
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.models.user import User
from src.models.group import Group
from src.models.expense import Expense
from src.services.expense_service import ExpenseService
from src.services.database_service import DatabaseService
from src.settings import get_settings
from src.logging_config import configure_logging
from src.template_engine import templates
from src.state import USERS, GROUPS
from src.routers.users import router as users_router
from src.routers.groups import router as groups_router
from src.routers.expenses import router as expenses_router
from src.routers.api_users import router as api_users_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_expenses import router as api_expenses_router

# App settings and logging
settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
configure_logging(settings.LOG_LEVEL)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-this-in-production")

def create_app() -> FastAPI:
    """Minimal application factory returning the configured FastAPI app.

    Keeps backward compatibility with tests that import `web_app.app` directly,
    while allowing other entrypoints to call `create_app()`.
    """
    return app

# Templates come from centralized template engine (with filters pre-registered)

# Static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Routers (preserve existing URLs)
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(expenses_router)

# API routers with JSON responses
app.include_router(api_users_router)
app.include_router(api_groups_router)
app.include_router(api_expenses_router)

# Helpers

def get_group_or_404(group_id: str) -> Group:
    group = GROUPS.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return group


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Render 404 with template when appropriate
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404,
        )
    # Fallback to default behavior for other HTTP errors
    raise exc


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled server error")
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500,
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

from src.auth import get_current_user_from_session, login_user, logout_user

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "users": list(USERS.values())}
    )

@app.post("/login")
async def login(request: Request, user_id: str = Form(...)):
    """Login user by setting session."""
    user = DatabaseService.get_user(user_id)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": list(USERS.values()), "error": "User not found"}
        )
    
    login_user(request, user)
    return RedirectResponse("/", status_code=303)

@app.post("/logout")
async def logout(request: Request):
    """Logout current user."""
    logout_user(request)
    return RedirectResponse("/login", status_code=303)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Check if user is authenticated
    current_user = get_current_user_from_session(request)
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    
    # Get user's groups and expenses
    user_groups = []
    user_expenses = []
    
    # Get all groups where the user is a member
    for group in GROUPS.values():
        if current_user.id in group.members:
            ExpenseService.recompute_group_balances(group)
            user_groups.append(group)
            # Get expenses created by this user, or fallback to paid_by for legacy data
            user_expenses.extend([
                exp for exp in group.expenses 
                if (exp.created_by == current_user.id) or 
                   (exp.created_by is None and exp.paid_by == current_user.id)
            ])
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "users": list(USERS.values()),
            "groups": user_groups,
            "user_expenses": user_expenses,
            # Total number of expenses created by this user
            "total_expenses": len(user_expenses),
        },
    )


