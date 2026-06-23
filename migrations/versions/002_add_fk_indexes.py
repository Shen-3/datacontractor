"""add missing foreign key indexes

Revision ID: 002_add_fk_indexes
Revises: 001_initial
Create Date: 2026-06-23 00:00:00.000000
"""

from alembic import op

revision = "002_add_fk_indexes"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # contract_versions
    op.create_index("ix_contract_versions_contract_id", "contract_versions", ["contract_id"])

    # validation_runs
    op.create_index("ix_validation_runs_contract_id", "validation_runs", ["contract_id"])
    op.create_index("ix_validation_runs_contract_version_id", "validation_runs", ["contract_version_id"])
    op.create_index("ix_validation_runs_started_at", "validation_runs", ["started_at"])

    # violations
    op.create_index("ix_violations_validation_run_id", "violations", ["validation_run_id"])
    op.create_index("ix_violations_severity", "violations", ["severity"])
    op.create_index("ix_violations_status", "violations", ["status"])


def downgrade() -> None:
    op.drop_index("ix_contract_versions_contract_id")
    op.drop_index("ix_validation_runs_contract_id")
    op.drop_index("ix_validation_runs_contract_version_id")
    op.drop_index("ix_validation_runs_started_at")
    op.drop_index("ix_violations_validation_run_id")
    op.drop_index("ix_violations_severity")
    op.drop_index("ix_violations_status")
