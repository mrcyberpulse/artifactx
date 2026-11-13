from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.modules.workspaces.models import Role
from app.modules.sbom.models import Component

router = APIRouter(prefix="/workspaces/{workspace_id}/analytics", tags=["Analytics"])

@router.get("/licenses")
def get_license_stats(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    stmt = (
        select(Component.license, func.count(Component.id).label("count"))
        .where(Component.workspace_id == ctx.workspace.id)
        .group_by(Component.license)
    )
    results = db.execute(stmt).all()
    
    total = sum(r.count for r in results)
    data = []
    for license_name, count in results:
        name = license_name or "Unknown"
        percentage = round((count / total * 100), 1) if total > 0 else 0
        data.append({"name": name, "count": count, "percentage": percentage})
    
    return {"total": total, "licenses": data}

@router.get("/risk-distribution")
def get_risk_distribution(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    from app.modules.vulnerabilities.models import Finding, Advisory
    
    stmt = (
        select(Advisory.severity, func.count(Finding.id).label("count"))
        .join(Finding, Finding.advisory_id == Advisory.id)
        .where(Finding.workspace_id == ctx.workspace.id)
        .group_by(Advisory.severity)
    )
    results = db.execute(stmt).all()
    
    # Initialize with zeroes
    distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for severity, count in results:
        sev = severity or "UNKNOWN"
        if sev in distribution:
            distribution[sev] = count
        else:
            distribution["UNKNOWN"] += count
            
    return distribution
