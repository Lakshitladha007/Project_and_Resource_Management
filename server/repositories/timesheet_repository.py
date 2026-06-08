from datetime import date

from sqlalchemy.orm import Session, joinedload

from server.models.timesheet import Timesheet, TimesheetEntry
from server.repositories.base_repository import BaseRepository


class TimesheetRepository(BaseRepository[Timesheet]):
    def __init__(self, db: Session):
        super().__init__(Timesheet, db)

    def get_for_employee_week(
        self, employee_id: int, week_start: date
    ) -> Timesheet | None:
        return (
            self.db.query(Timesheet)
            .filter(
                Timesheet.employee_id == employee_id,
                Timesheet.week_start == week_start,
            )
            .first()
        )

    def list_for_employee(self, employee_id: int) -> list[Timesheet]:
        return (
            self.db.query(Timesheet)
            .filter(Timesheet.employee_id == employee_id)
            .order_by(Timesheet.week_start.desc())
            .all()
        )

    def get_with_entries(
        self, employee_id: int, week_start: date
    ) -> Timesheet | None:
        return (
            self.db.query(Timesheet)
            .options(
                joinedload(Timesheet.entries).joinedload(TimesheetEntry.tags),
            )
            .filter(
                Timesheet.employee_id == employee_id,
                Timesheet.week_start == week_start,
            )
            .first()
        )
