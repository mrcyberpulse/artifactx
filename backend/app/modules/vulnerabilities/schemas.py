import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any

class AdvisoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    source: str
    external_id: str
    title: str | None
    severity: str | None
    cvss_score: float | None
    is_kev: bool

class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    component_id: uuid.UUID
    advisory_id: uuid.UUID
    status: str
    risk_score: int
    risk_factors: dict[str, Any]
    advisory: AdvisoryOut

class RemediationTaskCreate(BaseModel):
    finding_id: uuid.UUID
    title: str
    description: str | None = None
    priority: str = "medium"
    due_date: datetime | None = None

class RemediationTaskUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    assignee_id: uuid.UUID | None = None

class RemediationTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    finding_id: uuid.UUID
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    created_at: datetime
