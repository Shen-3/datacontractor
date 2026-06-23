"""add ON DELETE CASCADE to contract_versions -> validation_runs FK

Revision ID: 003_fix_cascade
Revises: 002_add_fk_indexes
Create Date: 2026-06-23 00:00:00.000000
"""

from alembic import op

revision = "003_fix_cascade"
down_revision = "002_add_fk_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing FK and re-create with ON DELETE CASCADE so that
    # removing a ContractVersion cleans up its ValidationRun records.
    op.drop_constraint(
        "validation_runs_contract_version_id_fkey",
        "validation_runs",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "validation_runs_contract_version_id_fkey",
        "validation_runs",
        "contract_versions",
        ["contract_version_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "validation_runs_contract_version_id_fkey",
        "validation_runs",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "validation_runs_contract_version_id_fkey",
        "validation_runs",
        "contract_versions",
        ["contract_version_id"],
        ["id"],
    )
