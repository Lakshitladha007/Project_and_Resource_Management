"""skills and employee_skills tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.UniqueConstraint("name", name="uq_skills_name"),
    )
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("proficiency", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_employee_skills_employee"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name="fk_employee_skills_skill"
        ),
        sa.UniqueConstraint(
            "employee_id", "skill_id", name="uq_employee_skill"
        ),
    )


def downgrade() -> None:
    op.drop_table("employee_skills")
    op.drop_table("skills")
