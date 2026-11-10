import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, new_uuid


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class Criticality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_workspace_name", "workspace_id", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    environment: Mapped[str] = mapped_column(String(20), default=Environment.development.value, nullable=False)
    business_criticality: Mapped[str] = mapped_column(String(20), default=Criticality.medium.value, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
