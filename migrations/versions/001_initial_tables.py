"""initial tables

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("owner", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contract_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id"), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("schema_json", sa.JSON, nullable=True),
        sa.Column("quality_rules_json", sa.JSON, nullable=True),
        sa.Column("sla_json", sa.JSON, nullable=True),
        sa.Column("compatibility_mode", sa.String(50), server_default="backward"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "validation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id"), nullable=False),
        sa.Column(
            "contract_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contract_versions.id"),
            nullable=False,
        ),
        sa.Column("dataset_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_checked", sa.Integer, server_default=sa.text("0")),
        sa.Column("violations_count", sa.Integer, server_default=sa.text("0")),
    )

    op.create_table(
        "violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "validation_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("validation_runs.id"),
            nullable=False,
        ),
        sa.Column("contract_name", sa.String(255), nullable=False),
        sa.Column("contract_version", sa.String(50), nullable=False),
        sa.Column("check_name", sa.String(255), nullable=False),
        sa.Column("check_type", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(255), nullable=True),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="open"),
        sa.Column("failed_rows_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("sample_records_json", sa.JSON, nullable=True),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("violations")
    op.drop_table("validation_runs")
    op.drop_table("contract_versions")
    op.drop_table("contracts")
