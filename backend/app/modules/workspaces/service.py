import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import conflict
from app.modules.workspaces.models import Role, Workspace, WorkspaceMembership

_SLUG_SANITIZE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    base = _SLUG_SANITIZE.sub("-", name.lower()).strip("-") or "workspace"
    return base[:56]


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    slug = base
    suffix = 1
    while db.scalar(select(Workspace.id).where(Workspace.slug == slug)) is not None:
        suffix += 1
        slug = f"{base}-{suffix}"
        if suffix > 1000:
            raise conflict("Could not allocate a unique workspace slug.")
    return slug


def create_workspace(db: Session, *, name: str, description: str | None, owner_id: uuid.UUID) -> Workspace:
    workspace = Workspace(
        name=name, slug=unique_slug(db, name), description=description, created_by_id=owner_id
    )
    db.add(workspace)
    db.flush()
    db.add(WorkspaceMembership(workspace_id=workspace.id, user_id=owner_id, role=Role.owner.value))
    return workspace


def list_user_workspaces(db: Session, user_id: uuid.UUID) -> list[tuple[Workspace, str]]:
    rows = db.execute(
        select(Workspace, WorkspaceMembership.role)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(WorkspaceMembership.user_id == user_id)
        .order_by(Workspace.created_at)
    ).all()
    return [(w, role) for w, role in rows]


def get_membership(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMembership | None:
    return db.scalar(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
    )
