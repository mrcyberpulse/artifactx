import uuid
from datetime import datetime
from enum import Enum
from typing import Any
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin, new_uuid
from app.core.timeutil import utcnow

class FindingStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    ignored = "ignored"

class RemediationStatus(str, Enum):
    open = "open"
    assigned = "assigned"
    in_progress = "in_progress"
    awaiting_verification = "awaiting_verification"
    resolved = "resolved"

# 1. Vulnerability Advisory (Data from OSV, NVD, etc.)
class Advisory(Base, TimestampMixin):
    __tablename__ = "advisories"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., "osv", "nvd"
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g., "CVE-2023-1234"
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True) # CRITICAL, HIGH, MEDIUM, LOW
    epss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_kev: Mapped[bool] = mapped_column(Boolean, default=False) # CISA KEV
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

# 2. Vulnerability Finding (Link between Component and Advisory)
class Finding(Base, TimestampMixin):
    __tablename__ = "findings"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    component_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("components.id", ondelete="CASCADE"), nullable=False, index=True)
    advisory_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("advisories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(20), default=FindingStatus.open.value, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # 0-100
    risk_factors: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False) # Explainability
    matching_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    advisory: Mapped["Advisory"] = relationship()

# 3. Remediation Task
class RemediationTask(Base, TimestampMixin):
    __tablename__ = "remediation_tasks"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    finding_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=RemediationStatus.open.value, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    finding: Mapped["Finding"] = relationship()
