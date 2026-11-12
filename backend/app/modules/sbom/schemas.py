from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SBOMUploadResponse(BaseModel):
    import_id: uuid.UUID
    status: str
    message: str


class SBOMImportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    sbom_document_id: uuid.UUID | None
    source_filename: str
    detected_format: str | None
    status: str
    error_message: str | None
    component_count: int
    dependency_count: int
    started_at: datetime
    completed_at: datetime | None


class SBOMDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    name: str | None
    format: str
    spec_version: str | None
    file_hash_sha256: str
    source_filename: str
    created_at: datetime


class ComponentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sbom_document_id: uuid.UUID
    workspace_id: uuid.UUID
    project_id: uuid.UUID
    name: str
    version: str | None
    purl: str | None
    ecosystem: str | None
    supplier: str | None
    license: str | None
    component_type: str | None
    created_at: datetime


class ComponentDetailOut(ComponentOut):
    publisher: str | None
    sha256: str | None
    description: str | None
    sbom_ref: str | None
    raw_json: dict


class DependencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_ref: str
    target_ref: str
    relationship_type: str
