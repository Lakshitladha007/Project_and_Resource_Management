"""milestones table

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "milestones",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("story_points", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="NOT_STARTED",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name="fk_milestones_project"
        ),
    )


def downgrade() -> None:
    op.drop_table("milestones")
