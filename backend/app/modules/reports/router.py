import uuid
import csv
import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.modules.workspaces.models import Role
from app.modules.vulnerabilities.models import Finding

router = APIRouter(prefix="/workspaces/{workspace_id}/reports", tags=["Reports"])

@router.get("/export/csv")
def export_csv(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    findings = db.scalars(select(Finding).where(Finding.workspace_id == ctx.workspace.id)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Finding ID", "CVE", "Severity", "Risk Score", "Status"])
    for f in findings:
        writer.writerow([f.id, f.advisory.external_id, f.advisory.severity, f.risk_score, f.status])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=artifactx_report_{ctx.workspace.id}.csv"}
    )
