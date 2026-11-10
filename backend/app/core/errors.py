import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("artifactx.errors")


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.headers = headers


def unauthorized(message: str = "Authentication required.") -> AppError:
    return AppError(401, "unauthorized", message, headers={"WWW-Authenticate": "Bearer"})


def forbidden(message: str = "You do not have permission to perform this action.") -> AppError:
    return AppError(403, "forbidden", message)


def not_found(resource: str = "Resource") -> AppError:
    return AppError(404, "not_found", f"{resource} not found.")


def conflict(message: str) -> AppError:
    return AppError(409, "conflict", message)


def bad_request(code: str, message: str) -> AppError:
    return AppError(400, code, message)


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse, "description": "Missing or invalid credentials."},
    403: {"model": ErrorResponse, "description": "Insufficient workspace role."},
    404: {"model": ErrorResponse, "description": "Not found, or not visible to the caller."},
    422: {"model": ErrorResponse, "description": "Validation error."},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded."},
}


def _payload(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict:
    body: dict[str, Any] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return {"error": body}


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(exc.code, exc.message, exc.details),
        headers=exc.headers,
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Only field location and message are returned: never echo submitted input (it may be a password).
    details = [
        {
            "field": ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path")),
            "message": str(err["msg"]),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422, content=_payload("validation_error", "Request validation failed.", details)
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    codes = {401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}
    code = codes.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(code, str(exc.detail)),
        headers=getattr(exc, "headers", None),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500, content=_payload("internal_error", "An internal error occurred.")
    )
