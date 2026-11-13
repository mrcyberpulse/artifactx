from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.core.errors import ERROR_RESPONSES, not_found
from app.core.pagination import Page, PageParams, build_page, page_params
from app.modules.audit.service import record
from app.modules.sbom import service as sbom_service
from app.modules.sbom.models import Component, SBOMDocument, SBOMImport
from app.modules.sbom.parsers.base import SBOMValidationError
from app.modules.sbom.schemas import (
    ComponentDetailOut,
    ComponentOut,
    DependencyOut,
    SBOMDocumentOut,
    SBOMImportOut,
    SBOMUploadResponse,
)
from app.modules.workspaces.models import Role

router = APIRouter(prefix="/workspaces/{workspace_id}/sbom", tags=["SBOM"])


# ── Upload ──────────────────────────────────────────────────────────────────
@router.post(
    "/upload",
    response_model=SBOMUploadResponse,
    status_code=202,
    summary="Upload an SBOM (CycloneDX JSON or SPDX JSON) to a project",
    responses=ERROR_RESPONSES,
)
def upload_sbom(
    project_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    ctx: WorkspaceContext = Depends(workspace_access(Role.member)),
    db: Session = Depends(get_db),
) -> SBOMUploadResponse:
    content = file.file.read()
    svc = sbom_service.SBOMIngestionService(db)
    try:
        import_row = svc.ingest(
            workspace_id=ctx.workspace.id,
            project_id=project_id,
            filename=file.filename or "upload.bin",
            content=content,
        )
    except SBOMValidationError as exc:
        raise from_validation_error(exc)

    record(
        db,
        action="sbom.imported",
        resource_type="sbom_import",
        resource_id=str(import_row.id),
        user_id=ctx.user.id,
        workspace_id=ctx.workspace.id,
        summary={
            "filename": import_row.source_filename,
            "status": import_row.status,
            "components": import_row.component_count,
        },
    )
    db.commit()

    return SBOMUploadResponse(
        import_id=import_row.id,
        status=import_row.status,
        message=(
            "SBOM imported successfully."
            if import_row.status == "completed"
            else f"Import finished with status: {import_row.status}."
        ),
    )


def from_validation_error(exc: SBOMValidationError):
    from app.core.errors import AppError

    return AppError(422, "invalid_sbom", str(exc))


# ── Import history ──────────────────────────────────────────────────────────
@router.get(
    "/imports",
    response_model=Page[SBOMImportOut],
    summary="List SBOM imports in this workspace",
    responses=ERROR_RESPONSES,
)
def list_imports(
    project_id: uuid.UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    params: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> dict:
    conditions = [SBOMImport.workspace_id == ctx.workspace.id]
    if project_id:
        conditions.append(SBOMImport.project_id == project_id)
    if status_filter:
        conditions.append(SBOMImport.status == status_filter)

    total = db.scalar(select(func.count(SBOMImport.id)).where(*conditions)) or 0
    rows = db.scalars(
        select(SBOMImport)
        .where(*conditions)
        .order_by(SBOMImport.started_at.desc())
        .limit(params.page_size)
        .offset(params.offset)
    ).all()
    return build_page(list(rows), total, params)


# ── SBOM documents ──────────────────────────────────────────────────────────
@router.get(
    "/documents",
    response_model=Page[SBOMDocumentOut],
    summary="List SBOM documents in this workspace",
    responses=ERROR_RESPONSES,
)
def list_documents(
    project_id: uuid.UUID | None = Query(default=None),
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    params: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> dict:
    conditions = [SBOMDocument.workspace_id == ctx.workspace.id]
    if project_id:
        conditions.append(SBOMDocument.project_id == project_id)

    total = db.scalar(select(func.count(SBOMDocument.id)).where(*conditions)) or 0
    rows = db.scalars(
        select(SBOMDocument)
        .where(*conditions)
        .order_by(SBOMDocument.created_at.desc())
        .limit(params.page_size)
        .offset(params.offset)
    ).all()
    return build_page(list(rows), total, params)


# ── Components ──────────────────────────────────────────────────────────────
@router.get(
    "/components",
    response_model=Page[ComponentOut],
    summary="List components in this workspace",
    responses=ERROR_RESPONSES,
)
def list_components(
    project_id: uuid.UUID | None = Query(default=None),
    sbom_document_id: uuid.UUID | None = Query(default=None),
    ecosystem: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    params: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> dict:
    conditions = [Component.workspace_id == ctx.workspace.id]
    if project_id:
        conditions.append(Component.project_id == project_id)
    if sbom_document_id:
        conditions.append(Component.sbom_document_id == sbom_document_id)
    if ecosystem:
        conditions.append(Component.ecosystem == ecosystem)
    if search:
        like = f"%{search.strip()}%"
        conditions.append(
            or_(
                Component.name.ilike(like),
                Component.purl.ilike(like),
                Component.version.ilike(like),
            )
        )

    total = db.scalar(select(func.count(Component.id)).where(*conditions)) or 0
    rows = db.scalars(
        select(Component)
        .where(*conditions)
        .order_by(Component.name, Component.version)
        .limit(params.page_size)
        .offset(params.offset)
    ).all()
    return build_page(list(rows), total, params)


@router.get(
    "/components/{component_id}",
    response_model=ComponentDetailOut,
    summary="Get component details",
    responses=ERROR_RESPONSES,
)
def get_component(
    component_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db),
) -> Component:
    comp = db.get(Component, component_id)
    if comp is None or comp.workspace_id != ctx.workspace.id:
        raise not_found("Component")
    return comp


@router.get(
    "/documents/{document_id}/dependencies",
    response_model=list[DependencyOut],
    summary="List dependency edges for an SBOM document",
    responses=ERROR_RESPONSES,
)
def list_dependencies(
    document_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db),
) -> list:
    doc = db.get(SBOMDocument, document_id)
    if doc is None or doc.workspace_id != ctx.workspace.id:
        raise not_found("SBOM document")
    return list(doc.dependencies)


# ── Delete import (cascades to document/components/deps) ────────────────────
@router.delete(
    "/imports/{import_id}",
    status_code=204,
    summary="Delete an SBOM import and its extracted data",
    responses=ERROR_RESPONSES,
)
def delete_import(
    import_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.admin)),
    db: Session = Depends(get_db),
) -> None:
    imp = db.get(SBOMImport, import_id)
    if imp is None or imp.workspace_id != ctx.workspace.id:
        raise not_found("SBOM import")

    if imp.sbom_document_id:
        doc = db.get(SBOMDocument, imp.sbom_document_id)
        if doc is not None:
            db.delete(doc)  # cascades to components + dependencies

    db.delete(imp)
    record(
        db,
        action="sbom.import_deleted",
        resource_type="sbom_import",
        resource_id=str(imp.id),
        user_id=ctx.user.id,
        workspace_id=ctx.workspace.id,
        summary={"filename": imp.source_filename},
    )
    db.commit()
@router.get("/graph")
def get_dependency_graph(
    project_id: uuid.UUID,
    ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)),
    db: Session = Depends(get_db)
):
    # Fetch all dependencies for this project
    deps = db.scalars(
        select(DependencyRelationship).where(
            DependencyRelationship.workspace_id == ctx.workspace.id,
            DependencyRelationship.project_id == project_id
        )
    ).all()

    # Fetch components to get actual names for the nodes
    comps = db.scalars(
        select(Component).where(
            Component.workspace_id == ctx.workspace.id,
            Component.project_id == project_id
        )
    ).all()
    
    # Create a lookup dictionary: sbom_ref -> component name
    comp_map = {c.sbom_ref: c.name for c in comps if c.sbom_ref}
    
    nodes = []
    edges = []
    added_nodes = set()

    for dep in deps:
        source_name = comp_map.get(dep.source_ref, dep.source_ref)
        target_name = comp_map.get(dep.target_ref, dep.target_ref)

        # Add source node
        if source_name not in added_nodes:
            nodes.append({"id": source_name, "label": source_name})
            added_nodes.add(source_name)
        
        # Add target node
        if target_name not in added_nodes:
            nodes.append({"id": target_name, "label": target_name})
            added_nodes.add(target_name)

        # Add edge
        edges.append({"source": source_name, "target": target_name})

    return {"nodes": nodes, "edges": edges}
