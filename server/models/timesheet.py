from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db.database import Base


class Timesheet(Base):
    __tablename__ = "timesheets"
    __table_args__ = (
        UniqueConstraint("employee_id", "week_start", name="uq_timesheets_employee_week"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    total_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    entries: Mapped[list["TimesheetEntry"]] = relationship(
        back_populates="timesheet", cascade="all, delete-orphan"
    )


class TimesheetEntry(Base):
    __tablename__ = "timesheet_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timesheet_id: Mapped[int] = mapped_column(
        ForeignKey("timesheets.id"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    hours: Mapped[int] = mapped_column(Integer, nullable=False)
    timesheet: Mapped["Timesheet"] = relationship(back_populates="entries")
    tags: Mapped[list["TimesheetEntryTag"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan"
    )


class ActivityTag(Base):
    __tablename__ = "activity_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)


class TimesheetEntryTag(Base):
    __tablename__ = "timesheet_entry_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timesheet_entry_id: Mapped[int] = mapped_column(
        ForeignKey("timesheet_entries.id"), nullable=False
    )
    activity_tag_id: Mapped[int | None] = mapped_column(
        ForeignKey("activity_tags.id"), nullable=True
    )
    custom_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entry: Mapped["TimesheetEntry"] = relationship(back_populates="tags")
