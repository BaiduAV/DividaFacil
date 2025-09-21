from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional, Union
import uuid
from datetime import datetime
import logging
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.models.user import User
from src.models.group import Group
from src.models.expense import Expense
from src.services.expense_service import ExpenseService
from src.settings import get_settings
from src.logging_config import configure_logging
from src.template_engine import templates
from src.state import USERS, GROUPS
from src.services.session_manager import SessionManager
from src.services.database_service import DatabaseService
from src.routers.users import router as users_router
from src.routers.groups import router as groups_router
from src.routers.expenses import router as expenses_router
from src.routers.auth import router as auth_router
from src.routers.api_users import router as api_users_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_expenses import router as api_expenses_router

# App settings and logging
settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
configure_logging(settings.LOG_LEVEL)

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
app.include_router(auth_router)
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


@app.get("/session-info")
async def session_info():
    """Get session management information for monitoring."""
    return SessionManager.get_session_info()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Check if user is authenticated
    user_id = SessionManager.get_user_id(request)
    current_user = None
    if user_id:
        current_user = DatabaseService.get_user(user_id)
    
    # If authenticated, show user's data only
    if current_user:
        # Get user's groups only
        user_groups = [g for g in GROUPS.values() if current_user.id in g.members]
        # Recompute balances for user's groups
        for g in user_groups:
            ExpenseService.recompute_group_balances(g)
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "current_user": current_user,
                "users": [current_user],  # Show only current user
                "groups": user_groups,
                "total_expenses": sum(len(g.expenses) for g in user_groups),
                "is_authenticated": True,
            },
        )
    else:
        # Show public view - no data, just auth forms
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "current_user": None,
                "users": [],
                "groups": [],
                "total_expenses": 0,
                "is_authenticated": False,
            },
        )


