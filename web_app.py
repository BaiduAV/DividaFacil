from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Optional

from src.services.database_service import DatabaseService
from src.settings import get_settings
from src.logging_config import configure_logging
from src.template_engine import templates
from src.auth import get_current_user_from_session
from src.routers.users import router as users_router
from src.routers.groups import router as groups_router
from src.routers.expenses import router as expenses_router
from src.routers.auth import router as auth_router
from src.routers.api_users import router as api_users_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_expenses import router as api_expenses_router
from src.routers.api_auth import router as api_auth_router
from src.routers.web_auth import router as web_auth_router  # added

logger = logging.getLogger(__name__)

# Constants
API_PREFIX = "/api/"
SESSION_COOKIE_NAME = "session_id"
HEALTH_CHECK_RESPONSE = {"status": "ok"}

class AppFactory:
    """Factory class for creating and configuring the FastAPI application."""

    def __init__(self):
        self.settings = get_settings()
        self._app: Optional[FastAPI] = None

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        if self._app is None:
            self._app = self._build_app()
        return self._app

    def _build_app(self) -> FastAPI:
        """Build the FastAPI application with all configurations."""
        app = FastAPI(title=self.settings.APP_NAME)

        # Configure logging
        configure_logging(self.settings.LOG_LEVEL)

        # Add middleware
        self._add_middleware(app)

        # Mount static files
        self._mount_static_files(app)

        # Include routers
        self._include_routers(app)

        # Add exception handlers
        self._add_exception_handlers(app)

        # Add health check endpoint
        self._add_health_check(app)

        # Add dashboard route
        self._add_dashboard_route(app)

        return app

    def _add_middleware(self, app: FastAPI) -> None:
        """Add middleware to the application."""
        app.add_middleware(
            SessionMiddleware,
            secret_key=self.settings.SESSION_SECRET_KEY,
            session_cookie=SESSION_COOKIE_NAME
        )

    def _mount_static_files(self, app: FastAPI) -> None:
        """Mount static files directory."""
        app.mount("/static", StaticFiles(directory=self.settings.STATIC_DIR), name="static")

    def _include_routers(self, app: FastAPI) -> None:
        """Include all application routers."""
        # Web routers
        routers = [
            web_auth_router,  # include web auth routes first
            auth_router,
            users_router,
            groups_router,
            expenses_router,
        ]

        # API routers
        api_routers = [
            api_users_router,
            api_groups_router,
            api_expenses_router,
            api_auth_router,
        ]

        for router in routers:
            app.include_router(router)

        for router in api_routers:
            app.include_router(router)

    def _add_exception_handlers(self, app: FastAPI) -> None:
        """Add exception handlers to the application."""

        @app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return await self._handle_http_exception(request, exc)

        @app.exception_handler(Exception)
        async def unhandled_exception_handler(request: Request, exc: Exception):
            return await self._handle_unhandled_exception(request, exc)

    async def _handle_http_exception(self, request: Request, exc: StarletteHTTPException) -> JSONResponse | HTMLResponse:
        """Handle HTTP exceptions with appropriate response format."""
        # For API requests, return JSON error responses
        if request.url.path.startswith(API_PREFIX):
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

    async def _handle_unhandled_exception(self, request: Request, exc: Exception) -> HTMLResponse:
        """Handle unhandled exceptions."""
        logger.exception("Unhandled server error")
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request},
            status_code=500,
        )

    def _add_health_check(self, app: FastAPI) -> None:
        """Add health check endpoint."""
        @app.get("/healthz")
        async def healthz():
            return HEALTH_CHECK_RESPONSE

    def _add_dashboard_route(self, app: FastAPI) -> None:
        """Add dashboard route."""
        from src.services.dashboard_service import DashboardService

        @app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            return await DashboardService.render_dashboard(request)


# Create application instance
app_factory = AppFactory()
app = app_factory.create_app()

def create_app() -> FastAPI:
    """Application factory function for backward compatibility."""
    return app_factory.create_app()
