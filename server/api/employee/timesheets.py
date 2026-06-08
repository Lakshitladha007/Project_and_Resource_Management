from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.timesheet import (
    ActivityTagResponse,
    EmployeeAllocationsListResponse,
    SubmitTimesheetRequest,
    TimesheetDetailResponse,
    TimesheetPreviewResponse,
    TimesheetReminderResponse,
    TimesheetSummaryResponse,
)
from server.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/employee", tags=["employee"])

employee_only = require_role(Role.EMPLOYEE.value)


@router.get("/reminder", response_model=TimesheetReminderResponse)
def get_reminder(
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> TimesheetReminderResponse:
    data = TimesheetService(db).get_reminder(current_user.id)
    return TimesheetReminderResponse(**data)


@router.get("/activity-tags", response_model=list[ActivityTagResponse])
def list_activity_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> list[ActivityTagResponse]:
    rows = TimesheetService(db).list_activity_tags()
    return [ActivityTagResponse(**row) for row in rows]


@router.get("/timesheets/preview", response_model=TimesheetPreviewResponse)
def preview_timesheet_week(
    week_start: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> TimesheetPreviewResponse:
    data = TimesheetService(db).preview_week(current_user.id, week_start)
    return TimesheetPreviewResponse(**data)


@router.post("/timesheets", response_model=TimesheetDetailResponse)
def submit_timesheet(
    payload: SubmitTimesheetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> TimesheetDetailResponse:
    entries = [entry.model_dump() for entry in payload.entries]
    data = TimesheetService(db).submit_timesheet(
        current_user.id, payload.week_start, entries
    )
    return TimesheetDetailResponse(**data)


@router.get("/timesheets", response_model=list[TimesheetSummaryResponse])
def list_my_timesheets(
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> list[TimesheetSummaryResponse]:
    rows = TimesheetService(db).list_timesheets(current_user.id)
    return [TimesheetSummaryResponse(**row) for row in rows]


@router.get("/timesheets/{week_start}", response_model=TimesheetDetailResponse)
def get_timesheet_detail(
    week_start: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> TimesheetDetailResponse:
    data = TimesheetService(db).get_timesheet_detail(current_user.id, week_start)
    return TimesheetDetailResponse(**data)


@router.get("/allocations", response_model=EmployeeAllocationsListResponse)
def list_my_allocations(
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_only),
) -> EmployeeAllocationsListResponse:
    data = TimesheetService(db).list_my_allocations(current_user.id)
    return EmployeeAllocationsListResponse(**data)
