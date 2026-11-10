import uuid

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import CurrentUser, current_user
from app.core.errors import ERROR_RESPONSES, bad_request, unauthorized
from app.core.rate_limit import RateLimiter, client_ip
from app.core.security import (
    burn_password_check,
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.timeutil import utcnow
from app.modules.audit.service import record
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE = "artifactx_refresh"
NATIVE_HEADER = "x-artifactx-client"

_login_limiter = RateLimiter("login", limit=10, window_seconds=60)
_register_limiter = RateLimiter("register", limit=5, window_seconds=300)
_reset_limiter = RateLimiter("password_reset", limit=5, window_seconds=300)


def _is_native(request: Request) -> bool:
    return request.headers.get(NATIVE_HEADER, "").lower() == "native"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        REFRESH_COOKIE,
        raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=settings.refresh_token_days * 86400,
        path="/api/auth",
    )


def _token_response(db: Session, user: User, request: Request, response: Response) -> TokenResponse:
    access_token, expires_in = create_access_token(user.id)
    raw_refresh, _ = auth_service.issue_refresh_token(
        db, user_id=user.id, user_agent=request.headers.get("user-agent")
    )
    native = _is_native(request)
    if native:
        response.headers["Cache-Control"] = "no-store"
    else:
        _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=raw_refresh if native else None,
        user=UserOut.model_validate(user),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user and sign in",
    responses=ERROR_RESPONSES,
)
def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    if not get_settings().registration_enabled:
        raise bad_request("registration_disabled", "Registration is currently disabled.")
    _register_limiter.check(client_ip(request))

    if db.scalar(select(User.id).where(User.email == body.email.lower())):
        # Same generic message as any other validation failure: do not confirm the email exists.
        raise bad_request("registration_failed", "Registration could not be completed.")

    user = User(
        email=body.email.lower(), full_name=body.full_name, password_hash=hash_password(body.password)
    )
    db.add(user)
    db.flush()
    record(db, action="auth.register", resource_type="user", resource_id=str(user.id), user_id=user.id, request=request)
    token_response = _token_response(db, user, request, response)
    db.commit()
    return token_response


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
    responses=ERROR_RESPONSES,
)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenResponse:
    _login_limiter.check(client_ip(request))

    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None:
        burn_password_check(body.password)
        raise unauthorized("Invalid email or password.")
    if not user.is_active or not verify_password(user.password_hash, body.password):
        raise unauthorized("Invalid email or password.")

    user.last_login_at = utcnow()
    record(db, action="auth.login", resource_type="user", resource_id=str(user.id), user_id=user.id, request=request)
    token_response = _token_response(db, user, request, response)
    db.commit()
    return token_response


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for a new access token (rotates the refresh token)",
    responses=ERROR_RESPONSES,
)
def refresh(
    body: RefreshRequest,
    request: Request,
    response: Response,
    cookie_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: Session = Depends(get_db),
) -> TokenResponse:
    raw_token = body.refresh_token if _is_native(request) else cookie_token
    if not raw_token:
        raise unauthorized("No refresh token provided.")

    stored = auth_service.find_refresh_token(db, raw_token)
    if stored is None:
        raise unauthorized("Invalid refresh token.")

    if stored.revoked_at is not None:
        # Reuse of an already-rotated/revoked token: treat the whole family as compromised.
        auth_service.revoke_family(db, stored.family_id)
        db.commit()
        raise unauthorized("Refresh token reuse detected. All sessions in this family were revoked.")

    if stored.expires_at < utcnow():
        raise unauthorized("Refresh token expired.")

    user = db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise unauthorized("Account is unavailable.")

    auth_service.revoke_token(db, stored)
    access_token, expires_in = create_access_token(user.id)
    raw_new, _ = auth_service.issue_refresh_token(
        db, user_id=user.id, family_id=stored.family_id, user_agent=request.headers.get("user-agent")
    )
    native = _is_native(request)
    if native:
        response.headers["Cache-Control"] = "no-store"
    else:
        _set_refresh_cookie(response, raw_new)
    db.commit()
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=raw_new if native else None,
        user=UserOut.model_validate(user),
    )


@router.post("/logout", status_code=204, summary="Revoke the current refresh token")
def logout(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    cookie_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: Session = Depends(get_db),
) -> None:
    raw_token = (body.refresh_token if body else None) if _is_native(request) else cookie_token
    if raw_token:
        stored = auth_service.find_refresh_token(db, raw_token)
        if stored and stored.revoked_at is None:
            auth_service.revoke_token(db, stored)
            db.commit()
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth")


@router.get("/me", response_model=UserOut, summary="Get the authenticated user", responses=ERROR_RESPONSES)
def me(user: CurrentUser = Depends(current_user)) -> User:
    return user


@router.post(
    "/password-reset/request",
    status_code=202,
    summary="Request a password reset link",
    responses=ERROR_RESPONSES,
)
def request_password_reset(body: PasswordResetRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    _reset_limiter.check(client_ip(request))
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is not None:
        raw = auth_service.create_password_reset_token(db, user.id)
        reset_url = f"{get_settings().frontend_url}/reset-password?token={raw}"
        from app.core.mail import get_mailer

        get_mailer().send_password_reset(user.email, reset_url)
        record(db, action="auth.password_reset_requested", resource_type="user", resource_id=str(user.id), user_id=user.id, request=request)
        db.commit()
    # Always return the same response, whether or not the email exists.
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post(
    "/password-reset/confirm",
    status_code=204,
    summary="Confirm a password reset using the emailed token",
    responses=ERROR_RESPONSES,
)
def confirm_password_reset(body: PasswordResetConfirm, request: Request, db: Session = Depends(get_db)) -> None:
    _reset_limiter.check(client_ip(request))
    token = auth_service.find_valid_reset_token(db, body.token)
    if token is None:
        raise bad_request("invalid_token", "This reset link is invalid or has expired.")

    user = db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise bad_request("invalid_token", "This reset link is invalid or has expired.")

    user.password_hash = hash_password(body.new_password)
    token.used_at = utcnow()
    record(db, action="auth.password_reset_completed", resource_type="user", resource_id=str(user.id), user_id=user.id, request=request)
    db.commit()
