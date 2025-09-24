from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import logging
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.services.database_service import DatabaseService
from src.settings import get_settings
from src.logging_config import configure_logging
from src.template_engine import templates
from src.state import USERS, GROUPS
from src.auth import get_current_user_from_session, login_user, logout_user
from src.routers.users import router as users_router
from src.routers.groups import router as groups_router
from src.routers.expenses import router as expenses_router
from src.routers.auth import router as auth_router
from src.routers.api_users import router as api_users_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_expenses import router as api_expenses_router
from src.routers.api_auth import router as api_auth_router
from src.services.expense_service import ExpenseService

# App settings and logging
settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
configure_logging(settings.LOG_LEVEL)

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY, session_cookie="session_id")

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
app.include_router(api_auth_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # For API requests, return JSON error responses
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP Error", "detail": exc.detail}
        )
    
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

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page."""
    try:
        # Get users from database instead of state to avoid issues
        users_dict = DatabaseService.get_all_users()
        users_list = list(users_dict.values())

        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": users_list}
        )
    except Exception as e:
        # If there's an error loading users, show empty list with error
        print(f"Error loading users for login page: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": [], "error": "Error loading users"}
        )

@app.post("/login")
async def login(request: Request, email: str = Form(...)):
    """Login user by setting session."""
    try:
        user = DatabaseService.get_user_by_email(email)
        if not user:
            # Get users for the dropdown again
            users_dict = DatabaseService.get_all_users()
            users_list = list(users_dict.values())

            return templates.TemplateResponse(
                "login.html",
                {"request": request, "users": users_list, "error": "User not found"}
            )

        login_user(request, user)
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "users": [], "error": f"Login failed: {str(e)}"}
        )

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
            "total_expenses": len(user_expenses),
            "is_authenticated": True,
        },
    )
