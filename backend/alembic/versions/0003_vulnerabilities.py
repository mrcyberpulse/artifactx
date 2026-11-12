"""add vulnerabilities and remediation tables

Revision ID: 0003_vulnerabilities
Revises: 0002_sbom
Create Date: 2026-11-12 10:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003_vulnerabilities"
down_revision: Union[str, None] = "0002_sbom"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "advisories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("epss_score", sa.Float(), nullable=True),
        sa.Column("is_kev", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_advisories"),
    )
    op.create_index("ix_advisories_source", "advisories", ["source"])
    op.create_index("ix_advisories_external_id", "advisories", ["external_id"])

    op.create_table(
        "findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("component_id", sa.Uuid(), nullable=False),
        sa.Column("advisory_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_factors", sa.JSON(), nullable=False),
        sa.Column("matching_confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["component_id"], ["components.id"], name="fk_findings_component_id_components", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["advisory_id"], ["advisories.id"], name="fk_findings_advisory_id_advisories", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_findings"),
    )
    op.create_index("ix_findings_workspace_id", "findings", ["workspace_id"])
    op.create_index("ix_findings_project_id", "findings", ["project_id"])
    op.create_index("ix_findings_component_id", "findings", ["component_id"])
    op.create_index("ix_findings_advisory_id", "findings", ["advisory_id"])

    op.create_table(
        "remediation_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("finding_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("assignee_id", sa.Uuid(), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"], name="fk_remediation_tasks_finding_id_findings", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], name="fk_remediation_tasks_assignee_id_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_remediation_tasks"),
    )

def downgrade() -> None:
    op.drop_table("remediation_tasks")
    op.drop_table("findings")
    op.drop_table("advisories")
