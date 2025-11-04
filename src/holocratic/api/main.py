"""FastAPI application factory for the Holocratic API."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from holocratic.config import Settings, get_settings

TenantResolver: ContextVar[str | None] = ContextVar("tenant_id", default=None)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches the tenant identifier to the request state."""

    def __init__(self, app: FastAPI, settings: Settings) -> None:
        super().__init__(app)
        self._settings = settings

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        tenant_id = self._resolve_tenant(request)

        if self._settings.enforce_tenant_presence and tenant_id is None:
            return JSONResponse(
                status_code=400,
                content={"detail": "Tenant identifier is required."},
            )

        tenant_to_use = tenant_id or self._settings.default_tenant
        token = TenantResolver.set(tenant_to_use)
        request.state.tenant_id = tenant_to_use

        try:
            response = await call_next(request)
        finally:
            TenantResolver.reset(token)

        return response

    def _resolve_tenant(self, request: Request) -> str | None:
        settings = self._settings
        if settings.multi_tenant_enabled:
            header_value = request.headers.get(settings.tenant_header)
            if header_value:
                return header_value
            cookie_value = request.cookies.get(settings.tenant_cookie_name)
            if cookie_value:
                return cookie_value
        return None


def get_current_tenant(default: str | None = None) -> str | None:
    """Return the tenant identifier stored in the current request context."""

    return TenantResolver.get(default)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory returning a configured :class:`FastAPI` instance."""

    settings = settings or get_settings()

    app = FastAPI(title="Holocratic API", version="0.1.0")
    app.add_middleware(TenantContextMiddleware, settings=settings)

    @app.get("/health", tags=["system"])  # pragma: no cover - trivial endpoint
    async def healthcheck() -> dict[str, str]:
        """Basic healthcheck endpoint used for load balancers and monitors."""

        return {"status": "ok"}

    return app


__all__ = [
    "create_app",
    "TenantContextMiddleware",
    "TenantResolver",
    "get_current_tenant",
]
