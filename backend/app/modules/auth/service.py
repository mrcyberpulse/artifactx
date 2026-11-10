import uuid
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_opaque_token, hash_token
from app.core.timeutil import utcnow
from app.modules.auth.models import PasswordResetToken, RefreshToken


def issue_refresh_token(
    db: Session, *, user_id: uuid.UUID, family_id: uuid.UUID | None = None, user_agent: str | None = None
) -> tuple[str, RefreshToken]:
    """Issues a refresh token. Pass the existing family_id when rotating, so reuse detection
    can revoke the whole family if an old token in it is ever presented again."""
    settings = get_settings()
    raw = generate_opaque_token()
    record = RefreshToken(
        user_id=user_id,
        family_id=family_id or uuid.uuid4(),
        token_hash=hash_token(raw),
        expires_at=utcnow() + timedelta(days=settings.refresh_token_days),
        user_agent=(user_agent or "")[:255] or None,
    )
    db.add(record)
    db.flush()
    return raw, record


def find_refresh_token(db: Session, raw_token: str) -> RefreshToken | None:
    from sqlalchemy import select

    return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token)))


def revoke_family(db: Session, family_id: uuid.UUID) -> None:
    from sqlalchemy import select

    tokens = db.scalars(
        select(RefreshToken).where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
    )
    now = utcnow()
    for t in tokens:
        t.revoked_at = now


def revoke_token(db: Session, token: RefreshToken) -> None:
    token.revoked_at = utcnow()


def create_password_reset_token(db: Session, user_id: uuid.UUID) -> str:
    settings = get_settings()
    raw = generate_opaque_token()
    db.add(
        PasswordResetToken(
            user_id=user_id,
            token_hash=hash_token(raw),
            expires_at=utcnow() + timedelta(minutes=settings.password_reset_minutes),
        )
    )
    return raw


def find_valid_reset_token(db: Session, raw_token: str) -> PasswordResetToken | None:
    from sqlalchemy import select

    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_token(raw_token)))
    if token is None or token.used_at is not None or token.expires_at < utcnow():
        return None
    return token
