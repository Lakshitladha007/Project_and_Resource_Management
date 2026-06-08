from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from server.core.enums import TimesheetStatus
from server.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from server.models.system_config import SystemConfig
from server.models.timesheet import Timesheet, TimesheetEntry, TimesheetEntryTag
from server.repositories.activity_tag_repository import ActivityTagRepository
from server.repositories.allocation_repository import AllocationRepository
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.project_repository import ProjectRepository
from server.repositories.timesheet_repository import TimesheetRepository

HISTORY_WEEKS = 8


def monday_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday())


def week_end(week_start: date) -> date:
    return week_start + timedelta(days=6)


def most_recent_completed_week_start(today: date | None = None) -> date:
    today = today or date.today()
    candidate = monday_of_week(today) - timedelta(days=7)
    while week_end(candidate) >= today:
        candidate -= timedelta(days=7)
    return candidate


class TimesheetService:
    def __init__(self, db: Session):
        self.db = db
        self.timesheets = TimesheetRepository(db)
        self.allocations = AllocationRepository(db)
        self.employees = EmployeeRepository(db)
        self.projects = ProjectRepository(db)
        self.activity_tags = ActivityTagRepository(db)

    def _get_employee_for_user(self, user_id: int):
        employee = self.employees.get_by_user_id(user_id)
        if employee is None:
            raise PermissionDeniedError("Employee profile not found")
        if not employee.is_active:
            raise PermissionDeniedError("Employee account is not active")
        return employee

    def _max_weekly_hours(self) -> int:
        config = self.db.query(SystemConfig).first()
        if config is None:
            return 40
        return config.max_weekly_hours

    def _validate_week_start(self, week_start: date) -> date:
        week_start = monday_of_week(week_start)
        if week_start.weekday() != 0:
            raise ValidationError("Week start must be a Monday")
        if week_start > monday_of_week(date.today()):
            raise ValidationError("Cannot submit a timesheet for a future week")
        return week_start

    def _allocations_for_week(self, employee_id: int, week_start: date) -> list:
        period_end = week_end(week_start)
        return self.allocations.list_for_employee_in_period(
            employee_id, week_start, period_end
        )

    def _had_allocations_in_week(self, employee_id: int, week_start: date) -> bool:
        return bool(self._allocations_for_week(employee_id, week_start))

    def _allocation_rows_for_week(self, employee_id: int, week_start: date) -> list:
        rows = self._allocations_for_week(employee_id, week_start)
        if not rows:
            raise ValidationError(
                "You had no project allocations during this week"
            )
        return rows

    def _max_hours_for_allocation(self, utilization_percent: int) -> int:
        max_weekly = self._max_weekly_hours()
        return int(max_weekly * utilization_percent / 100)

    def list_activity_tags(self) -> list[dict]:
        return [
            {
                "id": tag.id,
                "label": tag.label,
                "display_order": tag.display_order,
            }
            for tag in self.activity_tags.list_ordered()
        ]

    def get_reminder(self, user_id: int) -> dict:
        employee = self._get_employee_for_user(user_id)
        week_start = most_recent_completed_week_start()
        existing = self.timesheets.get_for_employee_week(employee.id, week_start)
        if existing is not None:
            return {"show_reminder": False, "week_start": week_start}
        if not self._had_allocations_in_week(employee.id, week_start):
            return {"show_reminder": False, "week_start": week_start}
        return {"show_reminder": True, "week_start": week_start}

    def preview_week(self, user_id: int, week_start: date | None = None) -> dict:
        employee = self._get_employee_for_user(user_id)
        if week_start is None:
            week_start = monday_of_week(date.today())
        else:
            week_start = self._validate_week_start(week_start)

        existing = self.timesheets.get_for_employee_week(employee.id, week_start)
        if existing is not None:
            raise ValidationError(
                f"Timesheet for week {week_start.isoformat()} already submitted"
            )

        allocation_rows = self._allocation_rows_for_week(employee.id, week_start)
        max_weekly = self._max_weekly_hours()
        projects = []
        for row in allocation_rows:
            project = self.projects.get(row.project_id)
            max_hours = self._max_hours_for_allocation(row.utilization_percent)
            projects.append(
                {
                    "project_id": row.project_id,
                    "project_name": project.name if project else str(row.project_id),
                    "utilization_percent": row.utilization_percent,
                    "max_hours": max_hours,
                }
            )
        return {
            "employee_name": employee.full_name,
            "week_start": week_start,
            "max_weekly_hours": max_weekly,
            "projects": projects,
        }

    def submit_timesheet(
        self,
        user_id: int,
        week_start: date,
        entries: list[dict],
    ) -> dict:
        employee = self._get_employee_for_user(user_id)
        week_start = self._validate_week_start(week_start)

        if self.timesheets.get_for_employee_week(employee.id, week_start):
            raise ValidationError("Timesheet for this week has already been submitted")

        allocation_rows = self._allocation_rows_for_week(employee.id, week_start)
        allocation_by_project = {row.project_id: row for row in allocation_rows}
        expected_project_ids = set(allocation_by_project)

        if not entries:
            raise ValidationError("At least one project entry is required")

        submitted_project_ids = {entry["project_id"] for entry in entries}
        unknown = submitted_project_ids - expected_project_ids
        if unknown:
            raise ValidationError("One or more projects are not allocated for this week")
        missing = expected_project_ids - submitted_project_ids
        if missing:
            raise ValidationError("Enter hours for every allocated project")

        max_weekly = self._max_weekly_hours()
        total_hours = 0
        parsed_entries: list[dict] = []

        for entry in entries:
            project_id = entry["project_id"]
            hours = entry["hours"]
            tags = entry.get("tags") or []

            if hours < 0:
                raise ValidationError("Hours cannot be negative")
            allocation = allocation_by_project[project_id]
            max_hours = self._max_hours_for_allocation(allocation.utilization_percent)
            if hours > max_hours:
                raise ValidationError(
                    f"Hours for project {project_id} exceed max {max_hours} "
                    f"({allocation.utilization_percent}% allocation)"
                )

            if hours > 0 and not tags:
                raise ValidationError("Select at least one activity tag when hours > 0")

            parsed_tags = []
            for tag in tags:
                if tag.get("custom_label"):
                    label = tag["custom_label"].strip()
                    if not label:
                        raise ValidationError("Custom activity tag cannot be empty")
                    parsed_tags.append({"custom_label": label})
                elif tag.get("activity_tag_id"):
                    activity_tag = self.activity_tags.get(tag["activity_tag_id"])
                    if activity_tag is None:
                        raise ValidationError("Invalid activity tag selected")
                    parsed_tags.append({"activity_tag_id": activity_tag.id})
                else:
                    raise ValidationError("Each tag must be preset or custom")

            total_hours += hours
            parsed_entries.append(
                {"project_id": project_id, "hours": hours, "tags": parsed_tags}
            )

        if total_hours > max_weekly:
            raise ValidationError(
                f"Total hours {total_hours} exceed weekly max {max_weekly}"
            )

        timesheet = Timesheet(
            employee_id=employee.id,
            week_start=week_start,
            total_hours=total_hours,
            submitted_at=datetime.utcnow(),
        )
        self.db.add(timesheet)
        self.db.flush()

        for parsed in parsed_entries:
            entry_row = TimesheetEntry(
                timesheet_id=timesheet.id,
                project_id=parsed["project_id"],
                hours=parsed["hours"],
            )
            self.db.add(entry_row)
            self.db.flush()
            for tag in parsed["tags"]:
                self.db.add(
                    TimesheetEntryTag(
                        timesheet_entry_id=entry_row.id,
                        activity_tag_id=tag.get("activity_tag_id"),
                        custom_label=tag.get("custom_label"),
                    )
                )

        self.db.commit()
        self.db.refresh(timesheet)
        return self.get_timesheet_detail(user_id, week_start)

    def list_timesheets(self, user_id: int) -> list[dict]:
        employee = self._get_employee_for_user(user_id)
        submitted = {
            row.week_start: row
            for row in self.timesheets.list_for_employee(employee.id)
        }
        end_week = most_recent_completed_week_start()
        start_week = end_week - timedelta(days=7 * (HISTORY_WEEKS - 1))

        rows: list[dict] = []
        seen_weeks: set[date] = set()
        current = start_week
        while current <= end_week:
            if current in submitted:
                sheet = submitted[current]
                rows.append(
                    {
                        "week_start": current,
                        "total_hours": sheet.total_hours,
                        "status": TimesheetStatus.SUBMITTED.value,
                    }
                )
                seen_weeks.add(current)
            elif self._had_allocations_in_week(employee.id, current):
                rows.append(
                    {
                        "week_start": current,
                        "total_hours": 0,
                        "status": TimesheetStatus.MISSED.value,
                    }
                )
                seen_weeks.add(current)
            current += timedelta(days=7)

        for week_start, sheet in submitted.items():
            if week_start not in seen_weeks:
                rows.append(
                    {
                        "week_start": week_start,
                        "total_hours": sheet.total_hours,
                        "status": TimesheetStatus.SUBMITTED.value,
                    }
                )

        rows.sort(key=lambda item: item["week_start"], reverse=True)
        return rows

    def get_timesheet_detail(self, user_id: int, week_start: date) -> dict:
        employee = self._get_employee_for_user(user_id)
        week_start = monday_of_week(week_start)
        sheet = self.timesheets.get_with_entries(employee.id, week_start)
        if sheet is None:
            raise NotFoundError("Timesheet not found for this week")

        entries = []
        for entry in sheet.entries:
            project = self.projects.get(entry.project_id)
            tag_labels = []
            for tag in entry.tags:
                if tag.custom_label:
                    tag_labels.append(tag.custom_label)
                elif tag.activity_tag_id:
                    activity_tag = self.activity_tags.get(tag.activity_tag_id)
                    if activity_tag:
                        tag_labels.append(activity_tag.label)
            entries.append(
                {
                    "project_id": entry.project_id,
                    "project_name": project.name if project else str(entry.project_id),
                    "hours": entry.hours,
                    "activity_tags": tag_labels,
                }
            )

        return {
            "week_start": sheet.week_start,
            "total_hours": sheet.total_hours,
            "status": TimesheetStatus.SUBMITTED.value,
            "entries": entries,
        }

    def list_my_allocations(self, user_id: int) -> dict:
        employee = self._get_employee_for_user(user_id)
        rows = self.allocations.list_active_for_employee(employee.id)

        allocations = []
        total_util = 0
        for row in rows:
            project = self.projects.get(row.project_id)
            allocations.append(
                {
                    "project_name": project.name if project else str(row.project_id),
                    "utilization_percent": row.utilization_percent,
                    "alloc_start": row.alloc_start,
                    "alloc_end": row.alloc_end,
                    "status": "ACTIVE",
                }
            )
            total_util += row.utilization_percent

        return {
            "allocations": allocations,
            "total_utilization": min(total_util, 100),
        }
