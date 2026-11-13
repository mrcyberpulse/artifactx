import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.errors import (
    AppError, app_error_handler, http_exception_handler, 
    unhandled_exception_handler, validation_error_handler
)
from app.core.middleware import SecurityHeadersMiddleware
from app.modules.audit.router import router as audit_router
from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.health.router import router as health_router
from app.modules.projects.router import router as projects_router
from app.modules.settings_info.router import router as settings_info_router
from app.modules.workspaces.router import router as workspaces_router
from app.modules.sbom.router import router as sbom_router
from app.modules.vulnerabilities.router import router as vuln_router
from app.modules.reports.router import router as reports_router

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=f"{settings.app_name} API",
    description=f"{settings.app_name} {settings.edition} API",
    version=settings.version,
    docs_url="/api/docs" if settings.docs_enabled else None,
    redoc_url="/api/redoc" if settings.docs_enabled else None,
    openapi_url="/api/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(SecurityHeadersMiddleware)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-ArtifactX-Client"],
    )

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

API_PREFIX = "/api"
app.include_router(health_router, prefix=API_PREFIX)
app.include_router(settings_info_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(workspaces_router, prefix=API_PREFIX)
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)
app.include_router(sbom_router, prefix=API_PREFIX)
app.include_router(vuln_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
