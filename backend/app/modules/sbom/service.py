from __future__ import annotations

import hashlib
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutil import utcnow
from app.modules.sbom.models import (
    Component,
    DependencyRelationship,
    SBOMDocument,
    SBOMImport,
)
from app.modules.sbom.parsers import detect_and_parse
from app.modules.sbom.parsers.base import ParsedSBOM, SBOMValidationError

logger = logging.getLogger("artifactx.sbom")

MAX_SBOM_BYTES = 25 * 1024 * 1024  # 25 MB


class SBOMIngestionService:
    def __init__(self, db: Session):
        self.db = db

    def ingest(
        self,
        *,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID,
        filename: str,
        content: bytes,
    ) -> SBOMImport:
        # Always create the import row first, so failed attempts are tracked.
        import_row = SBOMImport(
            workspace_id=workspace_id,
            project_id=project_id,
            source_filename=filename,
            status="processing",
            started_at=utcnow(),
        )
        self.db.add(import_row)
        self.db.flush()

        try:
            if len(content) > MAX_SBOM_BYTES:
                raise SBOMValidationError(
                    f"File exceeds maximum size of {MAX_SBOM_BYTES // (1024 * 1024)} MB."
                )

            parsed: ParsedSBOM = detect_and_parse(content, filename)
            import_row.detected_format = parsed.format

            file_hash = hashlib.sha256(content).hexdigest()

            # Idempotency: same project + same file hash = duplicate
            existing = self.db.scalar(
                select(SBOMDocument).where(
                    SBOMDocument.project_id == project_id,
                    SBOMDocument.file_hash_sha256 == file_hash,
                )
            )
            if existing:
                import_row.sbom_document_id = existing.id
                import_row.status = "duplicate"
                import_row.completed_at = utcnow()
                self.db.commit()
                return import_row

            doc = SBOMDocument(
                workspace_id=workspace_id,
                project_id=project_id,
                name=parsed.name,
                format=parsed.format,
                spec_version=parsed.spec_version,
                file_hash_sha256=file_hash,
                source_filename=filename,
                document_metadata=parsed.metadata,
            )
            self.db.add(doc)
            self.db.flush()

            for pc in parsed.components:
                self.db.add(
                    Component(
                        sbom_document_id=doc.id,
                        workspace_id=workspace_id,
                        project_id=project_id,
                        sbom_ref=pc.sbom_ref,
                        name=pc.name,
                        version=pc.version,
                        purl=pc.purl,
                        ecosystem=pc.ecosystem,
                        supplier=pc.supplier,
                        publisher=pc.publisher,
                        license=pc.license,
                        sha256=pc.sha256,
                        description=pc.description,
                        component_type=pc.component_type,
                        raw_json=pc.raw,
                    )
                )

            seen_edges: set[tuple[str, str]] = set()
            for pd in parsed.dependencies:
                for target in pd.depends_on:
                    if target == pd.ref:
                        continue
                    edge = (pd.ref, target)
                    if edge in seen_edges:
                        continue
                    seen_edges.add(edge)
                    self.db.add(
                        DependencyRelationship(
                            sbom_document_id=doc.id,
                            workspace_id=workspace_id,
                            project_id=project_id,
                            source_ref=pd.ref,
                            target_ref=target,
                        )
                    )

            import_row.sbom_document_id = doc.id
            import_row.component_count = len(parsed.components)
            import_row.dependency_count = len(seen_edges)
            import_row.status = "completed"
            import_row.completed_at = utcnow()
            self.db.commit()

            logger.info(
                "SBOM import %s completed: %d components, %d deps",
                import_row.id,
                import_row.component_count,
                import_row.dependency_count,
            )
            return import_row

        except SBOMValidationError as exc:
            self.db.rollback()
            fresh = self.db.get(SBOMImport, import_row.id)
            if fresh:
                fresh.status = "failed"
                fresh.error_message = str(exc)
                fresh.completed_at = utcnow()
                self.db.commit()
            raise
        except Exception:
            self.db.rollback()
            fresh = self.db.get(SBOMImport, import_row.id)
            if fresh:
                fresh.status = "failed"
                fresh.error_message = "Internal processing error."
                fresh.completed_at = utcnow()
                self.db.commit()
            logger.exception("Unexpected SBOM ingestion failure")
            raise
