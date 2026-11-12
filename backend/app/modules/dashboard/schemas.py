from pydantic import BaseModel
class MetricCard(BaseModel):
    value: int | None
    available: bool
class DashboardSummary(BaseModel):
    total_projects: MetricCard
