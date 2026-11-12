from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardSummary
from app.modules.workspaces.models import Role

router = APIRouter(prefix="/workspaces/{workspace_id}/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def summary(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    return service.get_summary(db, ctx.workspace.id)
