import uuid
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.rate_limit import client_ip
from app.modules.audit.models import AuditEvent

_SENSITIVE = ("password", "token", "secret", "authorization", "api_key", "apikey", "cookie")


def redact(data: Any) -> Any:
    """Recursively mask anything that looks like a credential before it is stored."""
    if isinstance(data, dict):
        return {
            k: "[redacted]" if any(s in str(k).lower() for s in _SENSITIVE) else redact(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [redact(v) for v in data]
    return data


def record(
    db: Session,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: uuid.UUID | None = None,
    workspace_id: uuid.UUID | None = None,
    summary: dict[str, Any] | None = None,
    request: Request | None = None,
) -> AuditEvent:
    """Adds an event to the current session. The caller commits, so the audit row and the
    business change are written in the same transaction."""
    event = AuditEvent(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        workspace_id=workspace_id,
        summary=redact(summary or {}),
        ip_address=client_ip(request) if request else None,
    )
    db.add(event)
    return event
