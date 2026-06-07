"""allocations table

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "allocations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("utilization_percent", sa.Integer(), nullable=False),
        sa.Column("alloc_start", sa.Date(), nullable=False),
        sa.Column("alloc_end", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_allocations_employee"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name="fk_allocations_project"
        ),
    )


def downgrade() -> None:
    op.drop_table("allocations")
