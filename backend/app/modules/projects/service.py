import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.pagination import PageParams
from app.modules.projects.models import Project


def list_projects(
    db: Session,
    workspace_id: uuid.UUID,
    *,
    search: str | None,
    environment: str | None,
    criticality: str | None,
    params: PageParams,
) -> tuple[list[Project], int]:
    conditions = [Project.workspace_id == workspace_id, Project.deleted_at.is_(None)]
    if search:
        like = f"%{search.strip()}%"
        conditions.append(or_(Project.name.ilike(like), Project.description.ilike(like)))
    if environment:
        conditions.append(Project.environment == environment)
    if criticality:
        conditions.append(Project.business_criticality == criticality)

    total = db.scalar(select(func.count(Project.id)).where(*conditions)) or 0
    items = list(
        db.scalars(
            select(Project)
            .where(*conditions)
            .order_by(Project.created_at.desc())
            .limit(params.page_size)
            .offset(params.offset)
        )
    )
    return items, total


def get_project(db: Session, workspace_id: uuid.UUID, project_id: uuid.UUID) -> Project | None:
    return db.scalar(
        select(Project).where(
            Project.id == project_id, Project.workspace_id == workspace_id, Project.deleted_at.is_(None)
        )
    )
