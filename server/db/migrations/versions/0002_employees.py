"""employees table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=60), nullable=True),
        sa.Column("designation", sa.String(length=60), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="BENCH"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_employees_user"),
        sa.ForeignKeyConstraint(
            ["manager_id"], ["users.id"], name="fk_employees_manager"
        ),
        sa.UniqueConstraint("user_id", name="uq_employees_user_id"),
    )


def downgrade() -> None:
    op.drop_table("employees")
