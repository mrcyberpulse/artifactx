import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.core.errors import ERROR_RESPONSES, not_found
from app.core.pagination import Page, PageParams, build_page, page_params
from app.core.timeutil import utcnow
from app.modules.audit.service import record
from app.modules.projects import service
from app.modules.projects.models import Criticality, Environment, Project
from app.modules.projects.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.modules.workspaces.models import Role

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["Projects"])


@router.get("", response_model=Page[ProjectOut], summary="List projects in a workspace", responses=ERROR_RESPONSES)
def list_projects(
    search: str | None = Query(default=None, max_length=120),
    environment: Environment | None = None,
    criticality: Criticality | None = None,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    params: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> dict:
    items, total = service.list_projects(
        db,
        ctx.workspace.id,
        search=search,
        environment=environment.value if environment else None,
        criticality=criticality.value if criticality else None,
        params=params,
    )
    return build_page(items, total, params)


@router.post(
    "", response_model=ProjectOut, status_code=201, summary="Create a project", responses=ERROR_RESPONSES
)
def create_project(
    body: ProjectCreate,
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db),
) -> Project:
    project = Project(
        workspace_id=ctx.workspace.id,
        name=body.name,
        description=body.description,
        repository_url=body.repository_url,
        owner_id=ctx.user.id,
        environment=body.environment.value,
        business_criticality=body.business_criticality.value,
    )
    db.add(project)
    db.flush()
    record(
        db,
        action="project.created",
        resource_type="project",
        resource_id=str(project.id),
        user_id=ctx.user.id,
        workspace_id=ctx.workspace.id,
        summary={"name": project.name},
    )
    db.commit()
    db.refresh(project)
    return project


@router.get(
    "/{project_id}", response_model=ProjectOut, summary="Get project details", responses=ERROR_RESPONSES
)
def get_project(
    project_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db),
) -> Project:
    project = service.get_project(db, ctx.workspace.id, project_id)
    if project is None:
        raise not_found("Project")
    return project


@router.patch(
    "/{project_id}", response_model=ProjectOut, summary="Update project metadata", responses=ERROR_RESPONSES
)
def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db),
) -> Project:
    project = service.get_project(db, ctx.workspace.id, project_id)
    if project is None:
        raise not_found("Project")

    changes = body.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(project, field, value.value if hasattr(value, "value") else value)

    if changes:
        record(
            db,
            action="project.updated",
            resource_type="project",
            resource_id=str(project.id),
            user_id=ctx.user.id,
            workspace_id=ctx.workspace.id,
            summary={"fields": list(changes.keys())},
        )
    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/{project_id}", status_code=204, summary="Delete a project (soft delete)", responses=ERROR_RESPONSES
)
def delete_project(
    project_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.admin)),
    db: Session = Depends(get_db),
) -> None:
    project = service.get_project(db, ctx.workspace.id, project_id)
    if project is None:
        raise not_found("Project")
    project.deleted_at = utcnow()
    record(
        db,
        action="project.deleted",
        resource_type="project",
        resource_id=str(project.id),
        user_id=ctx.user.id,
        workspace_id=ctx.workspace.id,
        summary={"name": project.name},
    )
    db.commit()
