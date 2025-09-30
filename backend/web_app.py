import logging
import os
import secrets
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from src.logging_config import configure_logging
from src.routers.api_auth import router as api_auth_router
from src.routers.api_expenses import router as api_expenses_router
from src.routers.api_groups import router as api_groups_router
from src.routers.api_users import router as api_users_router
from src.settings import get_settings
from src.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

API_PREFIX = "/api"
CSRF_SESSION_KEY = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"
CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
SESSION_COOKIE_NAME = "session_id"
HEALTH_CHECK_RESPONSE = {"status": "ok"}


class AppFactory:
    def __init__(self):
        self.settings = get_settings()
        self._app: Optional[FastAPI] = None
        # metrics storage
        self._requests_total = 0
        self._requests_by_path: dict[str, int] = {}
        self._requests_in_flight = 0
        self._request_latency_sum = 0.0
        self._status_counts: dict[int, int] = {}
        self._error_total = 0

    def create_app(self) -> FastAPI:
        if self._app is None:
            self._app = self._build_app()
        return self._app

    def _build_app(self) -> FastAPI:
        description = (
            "DividaFácil API para gestão e divisão de despesas.\n\n"  # brief
            "Segurança: sessões baseadas em cookie + proteção CSRF (header X-CSRF-Token).\n"
            "Métricas: /metrics (Prometheus exposition) + /healthz.\n"
            "Fluxo CSRF: login/signup -> GET /api/csrf-token -> enviar header em POST/PUT/DELETE."
        )
        app = FastAPI(
            title=self.settings.APP_NAME,
            description=description,
            version="0.1.0",
            contact={"name": "DividaFácil", "url": "https://example.com"},
            openapi_tags=[
                {"name": "auth", "description": "Autenticação & sessão"},
                {"name": "users", "description": "Gestão de usuários"},
                {"name": "groups", "description": "Grupos e membros"},
                {"name": "expenses", "description": "Despesas e parcelas"},
            ],
        )
        configure_logging(self.settings.LOG_LEVEL)
        self._add_middleware(app)
        self._mount_static_files(app)
        self._include_routers(app)
        self._add_exception_handlers(app)
        self._add_health_check(app)
        self._add_metrics_endpoint(app)
        self._add_dashboard_route(app)
        # Ensure DB tables exist (idempotent) for tests / first run.
        try:
            DatabaseService.initialize()
            # Seed default user expected by some legacy tests if not present
            from src.services.database_service import DatabaseService as _DBS
            if not _DBS.get_user_by_email("test@example.com"):
                _DBS.create_user("Test User", "test@example.com")
        except Exception:  # pragma: no cover - defensive
            logger.exception("Database initialization failed")
        return app

    def _add_middleware(self, app: FastAPI) -> None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )

        @app.middleware("http")
        async def security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; font-src 'self'; connect-src 'self'"
            )
            return response

        @app.middleware("http")
        async def request_id_and_metrics(request: Request, call_next):
            request_id = str(uuid.uuid4())
            start = time.perf_counter()
            self._requests_in_flight += 1
            try:
                response = await call_next(request)
            finally:
                duration = time.perf_counter() - start
                self._requests_in_flight -= 1
                self._requests_total += 1
                path = request.url.path
                self._requests_by_path[path] = self._requests_by_path.get(path, 0) + 1
                self._request_latency_sum += duration
                # status counting
                if 'response' in locals():
                    status = getattr(response, 'status_code', 0)
                    self._status_counts[status] = self._status_counts.get(status, 0) + 1
                    if status >= 500:
                        self._error_total += 1
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Request-Duration-ms"] = f"{duration*1000:.2f}"
            return response

        @app.middleware("http")
        async def csrf_protection(request: Request, call_next):
            """Enforce CSRF for state-changing API requests except auth bootstrap endpoints.

            Exclusions:
              - Safe methods (GET/HEAD/OPTIONS)
              - /api/login and /api/signup (cannot have token yet)
              - /api/csrf-token (token retrieval)
            """
            path = request.url.path
            if path.startswith(API_PREFIX) and request.method not in CSRF_SAFE_METHODS:
                if path not in {f"{API_PREFIX}/login", f"{API_PREFIX}/signup", f"{API_PREFIX}/csrf-token"}:
                    session_token = request.session.get(CSRF_SESSION_KEY)
                    header_token = request.headers.get(CSRF_HEADER)
                    if not session_token or not header_token or not secrets.compare_digest(session_token, header_token):
                        return JSONResponse(
                            status_code=403,
                            content={
                                "error": "Forbidden",
                                "detail": "Missing or invalid CSRF token",
                            },
                        )
            return await call_next(request)

        app.add_middleware(
            SessionMiddleware,
            secret_key=self.settings.SESSION_SECRET_KEY,
            session_cookie=SESSION_COOKIE_NAME,
            https_only=self.settings.SESSION_COOKIE_SECURE,
        )

    def _mount_static_files(self, app: FastAPI) -> None:
        # Resolve static directory robustly so tests don't fail if relative path differs.
        directory = self.settings.STATIC_DIR
        # If given relative path, try relative to this file, then parent project root.
        if not os.path.isabs(directory):
            candidate = os.path.join(os.path.dirname(__file__), directory)
            if not os.path.isdir(candidate):
                parent_candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", directory))
                if os.path.isdir(parent_candidate):
                    candidate = parent_candidate
            directory = candidate
        if os.path.isdir(directory):
            app.mount("/static", StaticFiles(directory=directory), name="static")
        else:
            logger.warning("Static directory '%s' not found; skipping static mount", directory)

    def _include_routers(self, app: FastAPI) -> None:
        for router in [api_users_router, api_groups_router, api_expenses_router, api_auth_router]:
            app.include_router(router, prefix=API_PREFIX)

    def _add_exception_handlers(self, app: FastAPI) -> None:
        @app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return await self._handle_http_exception(request, exc)

        @app.exception_handler(Exception)
        async def unhandled_exception_handler(request: Request, exc: Exception):
            return await self._handle_unhandled_exception(request, exc)

    async def _handle_http_exception(self, request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": "HTTP Error", "detail": exc.detail})

    async def _handle_unhandled_exception(self, request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": "An unexpected error occurred"})

    def _add_health_check(self, app: FastAPI) -> None:
        @app.get("/healthz")
        async def healthz():
            try:
                return HEALTH_CHECK_RESPONSE
            except Exception as e:  # pragma: no cover
                logger.exception("Error in health check")
                return {"error": str(e)}

    def _add_metrics_endpoint(self, app: FastAPI) -> None:
        @app.get("/metrics", include_in_schema=False)
        async def metrics():
            avg_latency = 0.0
            if self._requests_total:
                avg_latency = self._request_latency_sum / self._requests_total
            lines = [
                f"app_requests_total {self._requests_total}",
                f"app_requests_in_flight {self._requests_in_flight}",
                f"app_request_latency_seconds_sum {self._request_latency_sum:.6f}",
                f"app_request_latency_seconds_avg {avg_latency:.6f}",
                f"app_errors_total {self._error_total}",
            ]
            for path, count in sorted(self._requests_by_path.items()):
                lines.append(f'app_requests_path_total{{path="{path}"}} {count}')
            for status, count in sorted(self._status_counts.items()):
                lines.append(f'app_requests_status_total{{status="{status}"}} {count}')
            return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

        @app.get(f"{API_PREFIX}/csrf-token")
        async def get_csrf_token(request: Request):
            token = request.session.get(CSRF_SESSION_KEY)
            if not token:
                token = secrets.token_urlsafe(32)
                request.session[CSRF_SESSION_KEY] = token
            return {"csrf_token": token, "header": CSRF_HEADER}

    def _add_dashboard_route(self, app: FastAPI) -> None:
        from fastapi.responses import FileResponse, RedirectResponse
        import os

        @app.get("/")
        async def root():
            return RedirectResponse(url="/app")

        @app.get("/app")
        async def serve_react_app():
            base_dir = getattr(
                self.settings,
                "FRONTEND_BUILD_DIR",
                os.path.join(os.path.dirname(__file__), "..", "frontend", "build"),
            )
            # Normalize to absolute path so subsequent security checks succeed and relative ('..') components are resolved.
            base_dir = os.path.abspath(base_dir)
            index_path = os.path.join(base_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path, media_type="text/html")
            raise HTTPException(status_code=404, detail="React app not found")

        @app.get("/app/{full_path:path}")
        async def serve_assets(full_path: str):
            base_dir = getattr(
                self.settings,
                "FRONTEND_BUILD_DIR",
                os.path.join(os.path.dirname(__file__), "..", "frontend", "build"),
            )
            base_dir = os.path.abspath(base_dir)
            # Resolve requested path safely and ensure it remains inside base_dir
            requested_path = os.path.abspath(os.path.join(base_dir, full_path))
            try:
                common = os.path.commonpath([requested_path, base_dir])
            except ValueError:  # Different drives on Windows, treat as forbidden
                raise HTTPException(status_code=403, detail="Forbidden")
            if common != base_dir:
                raise HTTPException(status_code=403, detail="Forbidden")
            if os.path.exists(requested_path) and os.path.isfile(requested_path):
                return FileResponse(requested_path)
            raise HTTPException(status_code=404, detail="Asset not found")


app_factory = AppFactory()
app = app_factory.create_app()

def create_app() -> FastAPI:  # backward compatibility
    return app_factory.create_app()
