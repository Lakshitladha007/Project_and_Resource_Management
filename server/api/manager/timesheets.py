from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.timesheet import (
    ManagerTimesheetDetailResponse,
    TeamTimesheetListResponse,
    TeamTimesheetRowResponse,
)
from server.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/manager", tags=["manager"])

manager_only = require_role(Role.MANAGER.value)


@router.get("/timesheets", response_model=TeamTimesheetListResponse)
def list_team_timesheets(
    week_start: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> TeamTimesheetListResponse:
    data = TimesheetService(db).list_team_timesheets(current_user.id, week_start)
    return TeamTimesheetListResponse(
        week_start=data["week_start"],
        rows=[TeamTimesheetRowResponse(**row) for row in data["rows"]],
    )


@router.get(
    "/timesheets/employees/{employee_id}",
    response_model=ManagerTimesheetDetailResponse,
)
def get_team_employee_timesheet(
    employee_id: int,
    week_start: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> ManagerTimesheetDetailResponse:
    data = TimesheetService(db).get_team_employee_timesheet(
        current_user.id, employee_id, week_start
    )
    return ManagerTimesheetDetailResponse(**data)
