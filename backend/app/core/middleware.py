from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.core.config import get_settings

DOC_PATHS = ("/api/docs", "/api/redoc", "/api/openapi.json")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        headers = response.headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "no-referrer"
        headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if get_settings().cookie_secure:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if not request.url.path.startswith(DOC_PATHS):
            headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
            headers["Cache-Control"] = "no-store"
        return response
