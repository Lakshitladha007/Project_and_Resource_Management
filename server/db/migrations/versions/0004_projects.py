"""projects table

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="PLANNED"
        ),
        sa.Column("manager_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "total_story_points", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "health_status",
            sa.String(length=20),
            nullable=False,
            server_default="ON_TRACK",
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["manager_user_id"], ["users.id"], name="fk_projects_manager"
        ),
        sa.UniqueConstraint("name", name="uq_projects_name"),
    )


def downgrade() -> None:
    op.drop_table("projects")
