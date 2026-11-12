from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin, new_uuid
from app.core.timeutil import utcnow


class SBOMDocument(Base, TimestampMixin):
    __tablename__ = "sbom_documents"
    __table_args__ = (
        UniqueConstraint("project_id", "file_hash_sha256", name="uq_sbom_documents_project_hash"),
        Index("ix_sbom_documents_workspace_project", "workspace_id", "project_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    spec_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    document_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    components: Mapped[list["Component"]] = relationship(
        back_populates="sbom_document", cascade="all, delete-orphan"
    )
    dependencies: Mapped[list["DependencyRelationship"]] = relationship(
        back_populates="sbom_document", cascade="all, delete-orphan"
    )


class SBOMImport(Base, TimestampMixin):
    __tablename__ = "sbom_imports"
    __table_args__ = (Index("ix_sbom_imports_workspace_status", "workspace_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sbom_document_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sbom_documents.id", ondelete="SET NULL"), nullable=True
    )
    source_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    detected_format: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    component_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dependency_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Component(Base, TimestampMixin):
    __tablename__ = "components"
    __table_args__ = (
        Index("ix_components_workspace_project", "workspace_id", "project_id"),
        Index("ix_components_ecosystem_name", "ecosystem", "name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    sbom_document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("sbom_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)

    sbom_ref: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    version: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    purl: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)
    ecosystem: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    supplier: Mapped[str | None] = mapped_column(String(512), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(512), nullable=True)
    license: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    sbom_document: Mapped["SBOMDocument"] = relationship(back_populates="components")


class DependencyRelationship(Base):
    __tablename__ = "dependency_relationships"
    __table_args__ = (
        UniqueConstraint(
            "sbom_document_id",
            "source_ref",
            "target_ref",
            name="uq_dependency_relationships_sbom_edge",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sbom_document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("sbom_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    source_ref: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    target_ref: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(
        String(32), default="depends_on", nullable=False
    )

    sbom_document: Mapped["SBOMDocument"] = relationship(back_populates="dependencies")
