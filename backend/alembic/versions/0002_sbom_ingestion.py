"""sbom ingestion: documents, imports, components, dependency relationships

Revision ID: 0002_sbom
Revises: 0001_initial
Create Date: 2026-11-12 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_sbom"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sbom_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column("format", sa.String(length=32), nullable=False),
        sa.Column("spec_version", sa.String(length=32), nullable=True),
        sa.Column("file_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("source_filename", sa.String(length=512), nullable=False),
        sa.Column("document_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"],
            name="fk_sbom_documents_workspace_id_workspaces", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_sbom_documents_project_id_projects", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sbom_documents"),
        sa.UniqueConstraint(
            "project_id", "file_hash_sha256", name="uq_sbom_documents_project_hash"
        ),
    )
    op.create_index("ix_sbom_documents_workspace_id", "sbom_documents", ["workspace_id"])
    op.create_index("ix_sbom_documents_project_id", "sbom_documents", ["project_id"])
    op.create_index("ix_sbom_documents_file_hash_sha256", "sbom_documents", ["file_hash_sha256"])
    op.create_index(
        "ix_sbom_documents_workspace_project", "sbom_documents", ["workspace_id", "project_id"]
    )

    op.create_table(
        "sbom_imports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("sbom_document_id", sa.Uuid(), nullable=True),
        sa.Column("source_filename", sa.String(length=512), nullable=False),
        sa.Column("detected_format", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("component_count", sa.Integer(), nullable=False),
        sa.Column("dependency_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"],
            name="fk_sbom_imports_workspace_id_workspaces", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"],
            name="fk_sbom_imports_project_id_projects", ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sbom_document_id"], ["sbom_documents.id"],
            name="fk_sbom_imports_sbom_document_id_sbom_documents", ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sbom_imports"),
    )
    op.create_index("ix_sbom_imports_workspace_id", "sbom_imports", ["workspace_id"])
    op.create_index("ix_sbom_imports_project_id", "sbom_imports", ["project_id"])
    op.create_index("ix_sbom_imports_status", "sbom_imports", ["status"])
    op.create_index(
        "ix_sbom_imports_workspace_status", "sbom_imports", ["workspace_id", "status"]
    )

    op.create_table(
        "components",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sbom_document_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("sbom_ref", sa.String(length=1024), nullable=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("version", sa.String(length=255), nullable=True),
        sa.Column("purl", sa.String(length=1024), nullable=True),
        sa.Column("ecosystem", sa.String(length=64), nullable=True),
        sa.Column("supplier", sa.String(length=512), nullable=True),
        sa.Column("publisher", sa.String(length=512), nullable=True),
        sa.Column("license", sa.String(length=512), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("component_type", sa.String(length=64), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sbom_document_id"], ["sbom_documents.id"],
            name="fk_components_sbom_document_id_sbom_documents", ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_components"),
    )
    op.create_index("ix_components_sbom_document_id", "components", ["sbom_document_id"])
    op.create_index("ix_components_workspace_id", "components", ["workspace_id"])
    op.create_index("ix_components_project_id", "components", ["project_id"])
    op.create_index("ix_components_sbom_ref", "components", ["sbom_ref"])
    op.create_index("ix_components_name", "components", ["name"])
    op.create_index("ix_components_version", "components", ["version"])
    op.create_index("ix_components_purl", "components", ["purl"])
    op.create_index("ix_components_ecosystem", "components", ["ecosystem"])
    op.create_index(
        "ix_components_workspace_project", "components", ["workspace_id", "project_id"]
    )
    op.create_index("ix_components_ecosystem_name", "components", ["ecosystem", "name"])

    op.create_table(
        "dependency_relationships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sbom_document_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_ref", sa.String(length=1024), nullable=False),
        sa.Column("target_ref", sa.String(length=1024), nullable=False),
        sa.Column("relationship_type", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["sbom_document_id"], ["sbom_documents.id"],
            name="fk_dependency_relationships_sbom_document_id_sbom_documents",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_dependency_relationships"),
        sa.UniqueConstraint(
            "sbom_document_id", "source_ref", "target_ref",
            name="uq_dependency_relationships_sbom_edge",
        ),
    )
    op.create_index(
        "ix_dependency_relationships_sbom_document_id",
        "dependency_relationships", ["sbom_document_id"],
    )
    op.create_index(
        "ix_dependency_relationships_workspace_id",
        "dependency_relationships", ["workspace_id"],
    )
    op.create_index(
        "ix_dependency_relationships_project_id",
        "dependency_relationships", ["project_id"],
    )
    op.create_index(
        "ix_dependency_relationships_source_ref", "dependency_relationships", ["source_ref"]
    )
    op.create_index(
        "ix_dependency_relationships_target_ref", "dependency_relationships", ["target_ref"]
    )


def downgrade() -> None:
    op.drop_table("dependency_relationships")
    op.drop_table("components")
    op.drop_table("sbom_imports")
    op.drop_table("sbom_documents")
