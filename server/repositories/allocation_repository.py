from sqlalchemy.orm import Session

from server.models.allocation import Allocation
from server.repositories.base_repository import BaseRepository


class AllocationRepository(BaseRepository[Allocation]):
    def __init__(self, db: Session):
        super().__init__(Allocation, db)

    def list_active(
        self,
        employee_id: int | None = None,
        project_id: int | None = None,
    ) -> list[Allocation]:
        query = self.db.query(Allocation).filter(Allocation.is_active.is_(True))
        if employee_id is not None:
            query = query.filter(Allocation.employee_id == employee_id)
        if project_id is not None:
            query = query.filter(Allocation.project_id == project_id)
        return query.order_by(Allocation.alloc_start).all()

    def list_active_for_employee(self, employee_id: int) -> list[Allocation]:
        return self.list_active(employee_id=employee_id)

    def list_for_employee_in_period(
        self, employee_id: int, period_start: date, period_end: date
    ) -> list[Allocation]:
        rows = self.list_active_for_employee(employee_id)
        return [
            row
            for row in rows
            if row.alloc_start <= period_end and row.alloc_end >= period_start
        ]
