import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.modules.workspaces.models import Role
from app.modules.vulnerabilities import service as vuln_service
from app.modules.vulnerabilities.models import Finding
from app.modules.vulnerabilities.schemas import FindingOut

router = APIRouter(prefix="/workspaces/{workspace_id}/vulnerabilities", tags=["Vulnerabilities"])

@router.post("/scan")
def scan_project(
    project_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db)
):
    findings_count = vuln_service.run_mock_scan(db, ctx.workspace.id, project_id)
    return {"message": "Scan complete", "findings_created": findings_count}

@router.get("/findings", response_model=list[FindingOut])
def list_findings(
    project_id: uuid.UUID | None = None,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db)
):
    stmt = select(Finding).where(Finding.workspace_id == ctx.workspace.id)
    if project_id:
        stmt = stmt.where(Finding.project_id == project_id)
    return db.scalars(stmt.order_by(Finding.risk_score.desc())).all()
# ... purana code (imports, scan_project, list_findings) ...

from app.modules.vulnerabilities.schemas import RemediationTaskCreate, RemediationTaskOut, RemediationTaskUpdate

@router.post("/remediation/tasks", response_model=RemediationTaskOut)
def create_task(
    body: RemediationTaskCreate,
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db)
):
    return vuln_service.create_remediation_task(db, ctx.workspace.id, body.model_dump())

@router.get("/remediation/tasks", response_model=list[RemediationTaskOut])
def list_tasks(
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db)
):
    return vuln_service.list_remediation_tasks(db, ctx.workspace.id)

@router.patch("/remediation/tasks/{task_id}", response_model=RemediationTaskOut)
def update_task(
    task_id: uuid.UUID,
    body: RemediationTaskUpdate,
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db)
):
    task = vuln_service.update_remediation_task(db, ctx.workspace.id, task_id, body.model_dump(exclude_unset=True))
    if not task:
        from app.core.errors import not_found
        raise not_found("Task")
    return task
