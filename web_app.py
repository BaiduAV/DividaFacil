import logging
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from src.logging_config import configure_logging
from src.routers.api_auth import router as api_auth_router
from src.routers.api_expenses import router as api_expenses_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_users import router as api_users_router
from src.settings import get_settings

logger = logging.getLogger(__name__)

# Constants
API_PREFIX = "/api"
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

        # Include routers - API routes must come before static mounting for precedence
        self._include_routers(app)

        # Add exception handlers
        self._add_exception_handlers(app)

        # Add health check endpoint
        self._add_health_check(app)

        # Add catch-all route for React app (must be last)
        self._add_dashboard_route(app)

        return app

    def _add_middleware(self, app: FastAPI) -> None:
        """Add middleware to the application."""
        # Add CORS middleware for security and cross-origin requests
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",  # React dev server
                "http://127.0.0.1:3000",  # React dev server alternative
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
        
        # Add security headers middleware
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'"
            )
            return response

        # Session middleware
        app.add_middleware(
            SessionMiddleware,
            secret_key=self.settings.SESSION_SECRET_KEY,
            session_cookie=SESSION_COOKIE_NAME,
        )

    def _mount_static_files(self, app: FastAPI) -> None:
        """Mount static files directory."""
        app.mount("/static", StaticFiles(directory=self.settings.STATIC_DIR), name="static")
        # React assets are served via catch-all route

    def _include_routers(self, app: FastAPI) -> None:
        """Include all application routers."""
        # Only include API routers - React app handles frontend
        api_routers = [
            api_users_router,
            api_groups_router,
            api_expenses_router,
            api_auth_router,
        ]

        for router in api_routers:
            app.include_router(router, prefix=API_PREFIX)

    def _add_exception_handlers(self, app: FastAPI) -> None:
        """Add exception handlers to the application."""

        @app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return await self._handle_http_exception(request, exc)

        @app.exception_handler(Exception)
        async def unhandled_exception_handler(request: Request, exc: Exception):
            return await self._handle_unhandled_exception(request, exc)

    async def _handle_http_exception(
        self, request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions with JSON responses."""
        # Return JSON error responses for all requests (API and frontend)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP Error", "detail": exc.detail}
        )

    async def _handle_unhandled_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions."""
        logger.exception("Unhandled server error")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
        )

    def _add_health_check(self, app: FastAPI) -> None:
        """Add health check endpoint."""

        @app.get("/healthz")
        async def healthz():
            try:
                return HEALTH_CHECK_RESPONSE
            except Exception as e:
                logger.exception("Error in health check")
                return {"error": str(e)}

    def _add_dashboard_route(self, app: FastAPI) -> None:
        """Add route to serve React app."""
        from fastapi.responses import FileResponse, RedirectResponse
        import os

        @app.get("/")
        async def root():
            return RedirectResponse(url="/app")

        @app.get("/app")
        async def serve_react_app():
            index_path = "frontend/build/index.html"
            if os.path.exists(index_path):
                return FileResponse(index_path, media_type="text/html")
            raise HTTPException(status_code=404, detail="React app not found")

        @app.get("/app/{full_path:path}")
        async def serve_react_assets(full_path: str):
            file_path = os.path.join("frontend/build", full_path)
            if os.path.exists(file_path):
                return FileResponse(file_path)
            raise HTTPException(status_code=404, detail="Asset not found")


# Create application instance
app_factory = AppFactory()
app = app_factory.create_app()


def create_app() -> FastAPI:
    """Application factory function for backward compatibility."""
    return app_factory.create_app()
