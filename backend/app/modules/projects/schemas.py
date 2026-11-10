import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.projects.models import Criticality, Environment


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    repository_url: str | None = Field(default=None, max_length=500)
    environment: Environment = Environment.development
    business_criticality: Criticality = Criticality.medium

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name must not be blank.")
        return v

    @field_validator("repository_url")
    @classmethod
    def _validate_url(cls, v: str | None) -> str | None:
        if v and not (v.startswith("http://") or v.startswith("https://") or v.startswith("git@")):
            raise ValueError("Repository URL must be an http(s) or git URL.")
        return v


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    repository_url: str | None = Field(default=None, max_length=500)
    environment: Environment | None = None
    business_criticality: Criticality | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    repository_url: str | None
    owner_id: uuid.UUID | None
    environment: Environment
    business_criticality: Criticality
    created_at: datetime
    updated_at: datetime
