from fastapi import APIRouter, Request, Response, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

from src.services.auth_service import AuthService
from src.services.session_manager import SessionManager
from src.template_engine import templates

router = APIRouter(tags=["auth"])


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Show registration form."""
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )


@router.post("/register")
async def register_user(
    request: Request,
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    """Register a new user."""
    # Basic validation
    if len(password) < 6:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Password must be at least 6 characters long"}
        )
    
    if not name.strip():
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Name cannot be empty"}
        )
    
    # Try to register
    user = AuthService.register_user(name.strip(), email, password)
    if not user:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Email already registered"}
        )
    
    # Create session and redirect to dashboard
    redirect_response = RedirectResponse(url="/", status_code=303)
    SessionManager.create_session(redirect_response, user.id)
    return redirect_response


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Show login form."""
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@router.post("/login")
async def login_user(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    """Login a user."""
    user = AuthService.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password"}
        )
    
    # Create session and redirect to dashboard
    redirect_response = RedirectResponse(url="/", status_code=303)
    SessionManager.create_session(redirect_response, user.id)
    return redirect_response


@router.post("/logout")
async def logout_user(request: Request):
    """Logout a user."""
    redirect_response = RedirectResponse(url="/", status_code=303)
    SessionManager.destroy_session(request, redirect_response)
    return redirect_response