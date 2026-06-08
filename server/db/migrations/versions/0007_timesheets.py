"""timesheets, entries, activity tags

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ACTIVITY_TAGS = [
    "Backend API Development",
    "Microservices / Architecture",
    "Database Design & Queries",
    "WebSocket / Real-time Features",
    "Frontend Development",
    "Code Review / Mentoring",
    "Bug Fixing",
    "DevOps / Deployment",
    "Testing & QA",
    "Documentation",
]


def upgrade() -> None:
    op.create_table(
        "timesheets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("total_hours", sa.Integer(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], name="fk_timesheets_employee"
        ),
        sa.UniqueConstraint(
            "employee_id", "week_start", name="uq_timesheets_employee_week"
        ),
    )
    op.create_table(
        "timesheet_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timesheet_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("hours", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["timesheet_id"], ["timesheets.id"], name="fk_timesheet_entries_timesheet"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name="fk_timesheet_entries_project"
        ),
    )
    op.create_table(
        "activity_tags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("label", sa.String(120), nullable=False, unique=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
    )
    op.create_table(
        "timesheet_entry_tags",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timesheet_entry_id", sa.Integer(), nullable=False),
        sa.Column("activity_tag_id", sa.Integer(), nullable=True),
        sa.Column("custom_label", sa.String(120), nullable=True),
        sa.ForeignKeyConstraint(
            ["timesheet_entry_id"],
            ["timesheet_entries.id"],
            name="fk_entry_tags_entry",
        ),
        sa.ForeignKeyConstraint(
            ["activity_tag_id"],
            ["activity_tags.id"],
            name="fk_entry_tags_tag",
        ),
    )

    tags_table = sa.table(
        "activity_tags",
        sa.column("label", sa.String),
        sa.column("display_order", sa.Integer),
    )
    op.bulk_insert(
        tags_table,
        [
            {"label": label, "display_order": index + 1}
            for index, label in enumerate(ACTIVITY_TAGS)
        ],
    )


def downgrade() -> None:
    op.drop_table("timesheet_entry_tags")
    op.drop_table("activity_tags")
    op.drop_table("timesheet_entries")
    op.drop_table("timesheets")
