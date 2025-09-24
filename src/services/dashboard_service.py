"""Dashboard service for handling dashboard-related operations."""

from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import List, Dict, Any
import logging

from ..auth import get_current_user_from_session
from ..template_engine import templates
from ..state import USERS, GROUPS
from ..services.expense_service import ExpenseService
from ..models.user import User
from ..models.group import Group
from ..models.expense import Expense
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for handling dashboard-related operations."""

    # Constants
    LOGIN_REDIRECT_URL = "/login"
    REDIRECT_STATUS_CODE = 303

    @classmethod
    async def render_dashboard(cls, request: Request) -> RedirectResponse | HTMLResponse:
        """Render the main dashboard page or login page if unauthenticated."""
        current_user = cls._get_authenticated_user(request)
        if not current_user:
            # Show login page with available users (simple selection UX)
            users = list(USERS.values()) or list(DatabaseService.get_all_users().values())
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "users": users,
                    "current_user": None,
                    "error": None,
                }
            )
        try:
            dashboard_data = cls._prepare_dashboard_data(current_user)
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    **dashboard_data,
                    "current_user": current_user,
                }
            )
        except Exception:
            logger.exception("Error rendering dashboard")
            return templates.TemplateResponse(
                "errors/500.html",
                {"request": request},
                status_code=500,
            )

    @classmethod
    def _get_authenticated_user(cls, request: Request) -> User | None:
        """Get the current authenticated user from the session."""
        return get_current_user_from_session(request)

    @classmethod
    def _prepare_dashboard_data(cls, current_user: User) -> Dict[str, Any]:
        """Prepare all data needed for the dashboard."""
        user_groups = cls._get_user_groups(current_user)
        user_expenses = cls._get_user_expenses(current_user, user_groups)

        return {
            "users": list(USERS.values()),
            "groups": user_groups,
            "user_expenses": user_expenses,
            "total_expenses": len(user_expenses),
        }

    @classmethod
    def _get_user_groups(cls, current_user: User) -> List[Group]:
        """Get all groups where the user is a member."""
        user_groups = []
        for group in GROUPS.values():
            if current_user.id in group.members:
                ExpenseService.recompute_group_balances(group)
                user_groups.append(group)
        return user_groups

    @classmethod
    def _get_user_expenses(cls, current_user: User, user_groups: List[Group]) -> List[Expense]:
        """Get all expenses created by or paid by the user."""
        user_expenses = []
        for group in user_groups:
            group_expenses = [
                exp for exp in group.expenses
                if (exp.created_by == current_user.id) or
                   (exp.created_by is None and exp.paid_by == current_user.id)
            ]
            user_expenses.extend(group_expenses)
        return user_expenses
