import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.core.errors import ERROR_RESPONSES
from app.core.pagination import Page, PageParams, build_page, page_params
from app.modules.audit.models import AuditEvent
from app.modules.users.models import User
from app.modules.workspaces.models import Role

router = APIRouter(tags=["Audit"])


class AuditEventOut(BaseModel):
    id: uuid.UUID
    action: str
    resource_type: str
    resource_id: str | None
    summary: dict
    actor_name: str | None
    created_at: datetime


@router.get(
    "/workspaces/{workspace_id}/audit-events",
    response_model=Page[AuditEventOut],
    summary="List workspace audit events (admin or owner)",
    responses=ERROR_RESPONSES,
)
def list_audit_events(
    action: str | None = Query(None, max_length=80, description="Exact action filter."),
    ctx: WorkspaceContext = Depends(workspace_access(Role.admin)),
    params: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> dict:
    conditions = [AuditEvent.workspace_id == ctx.workspace.id]
    if action:
        conditions.append(AuditEvent.action == action)
    total = db.scalar(select(func.count(AuditEvent.id)).where(*conditions)) or 0
    rows = db.execute(
        select(AuditEvent, User.full_name)
        .outerjoin(User, AuditEvent.user_id == User.id)
        .where(*conditions)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id)
        .limit(params.page_size)
        .offset(params.offset)
    ).all()
    items = [
        AuditEventOut(
            id=e.id,
            action=e.action,
            resource_type=e.resource_type,
            resource_id=e.resource_id,
            summary=e.summary,
            actor_name=name,
            created_at=e.created_at,
        )
        for e, name in rows
    ]
    return build_page(items, total, params)
