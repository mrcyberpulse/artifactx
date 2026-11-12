import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.vulnerabilities.models import Advisory, Finding, FindingStatus, RemediationTask
from app.modules.vulnerabilities.risk_engine import calculate_risk_score
from app.modules.sbom.models import Component

def run_mock_scan(db: Session, workspace_id: uuid.UUID, project_id: uuid.UUID) -> int:
    components = db.scalars(
        select(Component).where(
            Component.workspace_id == workspace_id,
            Component.project_id == project_id
        )
    ).all()

    findings_created = 0

    for comp in components:
        adv_data = None
        if comp.name.lower() == "lodash" and comp.version and comp.version.startswith("4.17.20"):
            adv_data = {
                "external_id": "CVE-2021-23337",
                "title": "Command Injection in lodash",
                "description": "lodash versions prior to 4.17.21 are vulnerable to Command Injection.",
                "cvss_score": 7.2,
                "severity": "HIGH",
                "is_kev": False,
            }
        elif comp.name.lower() == "express" and comp.version and comp.version.startswith("4.17.1"):
            adv_data = {
                "external_id": "CVE-2022-24999",
                "title": "qs prototype pollution in express",
                "description": "qs before 6.10.3, as used in Express, allows attackers to cause a denial of service.",
                "cvss_score": 7.5,
                "severity": "HIGH",
                "is_kev": False,
            }

        if adv_data:
            advisory = db.scalar(select(Advisory).where(Advisory.external_id == adv_data["external_id"]))
            if not advisory:
                advisory = Advisory(
                    source="mock-osv",
                    external_id=adv_data["external_id"],
                    title=adv_data["title"],
                    description=adv_data["description"],
                    cvss_score=adv_data["cvss_score"],
                    severity=adv_data["severity"],
                    is_kev=adv_data["is_kev"],
                )
                db.add(advisory)
                db.flush()

            existing_finding = db.scalar(
                select(Finding).where(Finding.component_id == comp.id, Finding.advisory_id == advisory.id)
            )
            
            if not existing_finding:
                risk_score, risk_factors = calculate_risk_score(
                    cvss_score=advisory.cvss_score,
                    is_kev=advisory.is_kev,
                    epss_score=0.05,
                    is_direct_dependency=True,
                    project_criticality="high"
                )
                
                finding = Finding(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    component_id=comp.id,
                    advisory_id=advisory.id,
                    status=FindingStatus.open.value,
                    risk_score=risk_score,
                    risk_factors=risk_factors,
                    matching_confidence=0.95
                )
                db.add(finding)
                findings_created += 1

    db.commit()
    return findings_created

def create_remediation_task(db: Session, workspace_id: uuid.UUID, data: dict) -> RemediationTask:
    task = RemediationTask(
        workspace_id=workspace_id,
        finding_id=data["finding_id"],
        title=data["title"],
        description=data.get("description"),
        priority=data.get("priority", "medium"),
        due_date=data.get("due_date"),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def list_remediation_tasks(db: Session, workspace_id: uuid.UUID) -> list[RemediationTask]:
    return db.scalars(
        select(RemediationTask)
        .where(RemediationTask.workspace_id == workspace_id)
        .order_by(RemediationTask.created_at.desc())
    ).all()

def update_remediation_task(db: Session, workspace_id: uuid.UUID, task_id: uuid.UUID, data: dict) -> RemediationTask | None:
    task = db.scalar(select(RemediationTask).where(
        RemediationTask.id == task_id, 
        RemediationTask.workspace_id == workspace_id
    ))
    if not task:
        return None
    
    for key, value in data.items():
        if value is not None:
            setattr(task, key, value)
            
    db.commit()
    db.refresh(task)
    return task
