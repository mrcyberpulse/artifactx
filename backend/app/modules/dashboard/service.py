import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.dashboard.schemas import DashboardSummary, MetricCard
from app.modules.projects.models import Project

def get_summary(db: Session, workspace_id: uuid.UUID) -> DashboardSummary:
    total = db.scalar(select(func.count(Project.id)).where(Project.workspace_id == workspace_id, Project.deleted_at.is_(None))) or 0
    return DashboardSummary(total_projects=MetricCard(value=total, available=True))
