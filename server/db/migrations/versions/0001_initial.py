"""initial: users and system_config

Revision ID: 0001
Revises:
Create Date: 2026-06-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "force_password_change",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "system_config",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "llm_provider", sa.String(length=20), nullable=False, server_default="GEMINI"
        ),
        sa.Column(
            "llm_api_key_encrypted",
            sa.String(length=512),
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "scheduler_interval_hours",
            sa.Integer(),
            nullable=False,
            server_default="6",
        ),
        sa.Column(
            "max_weekly_hours", sa.Integer(), nullable=False, server_default="40"
        ),
    )


def downgrade() -> None:
    op.drop_table("system_config")
    op.drop_table("users")
