import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser, current_user
from app.core.errors import ERROR_RESPONSES
from app.modules.audit.service import record
from app.modules.workspaces import service
from app.modules.workspaces.models import Role
from app.modules.workspaces.schemas import WorkspaceCreate, WorkspaceOut

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=list[WorkspaceOut], summary="List workspaces the caller belongs to")
def list_workspaces(user: CurrentUser = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = service.list_user_workspaces(db, user.id)
    return [
        {
            "id": w.id,
            "name": w.name,
            "slug": w.slug,
            "description": w.description,
            "role": role,
            "created_at": w.created_at,
        }
        for w, role in rows
    ]


@router.post(
    "",
    response_model=WorkspaceOut,
    status_code=201,
    summary="Create a workspace (caller becomes owner)",
    responses=ERROR_RESPONSES,
)
def create_workspace(
    body: WorkspaceCreate, user: CurrentUser = Depends(current_user), db: Session = Depends(get_db)
) -> dict:
    workspace = service.create_workspace(
        db, name=body.name, description=body.description, owner_id=user.id
    )
    record(
        db,
        action="workspace.created",
        resource_type="workspace",
        resource_id=str(workspace.id),
        user_id=user.id,
        workspace_id=workspace.id,
        summary={"name": workspace.name},
    )
    db.commit()
    db.refresh(workspace)
    return {
        "id": workspace.id,
        "name": workspace.name,
        "slug": workspace.slug,
        "description": workspace.description,
        "role": Role.owner,
        "created_at": workspace.created_at,
    }
