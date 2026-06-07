from datetime import date

from sqlalchemy.orm import Session

from server.core.enums import EmployeeStatus, ProjectStatus
from server.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from server.models.allocation import Allocation
from server.repositories.allocation_repository import AllocationRepository
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.project_repository import ProjectRepository

ALLOWED_PROJECT_STATUSES = {
    ProjectStatus.PLANNED.value,
    ProjectStatus.ACTIVE.value,
}


def _dates_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return start_a <= end_b and start_b <= end_a


class AllocationService:
    def __init__(self, db: Session):
        self.db = db
        self.allocations = AllocationRepository(db)
        self.employees = EmployeeRepository(db)
        self.projects = ProjectRepository(db)

    def _allocation_row(self, row: Allocation) -> dict:
        employee = self.employees.get(row.employee_id)
        project = self.projects.get(row.project_id)
        return {
            "id": row.id,
            "employee_id": row.employee_id,
            "employee_name": employee.full_name if employee else str(row.employee_id),
            "project_id": row.project_id,
            "project_name": project.name if project else str(row.project_id),
            "utilization_percent": row.utilization_percent,
            "alloc_start": row.alloc_start,
            "alloc_end": row.alloc_end,
        }

    def list_allocations(
        self,
        employee_id: int | None = None,
        project_id: int | None = None,
    ) -> list[dict]:
        rows = self.allocations.list_active(
            employee_id=employee_id, project_id=project_id
        )
        return [self._allocation_row(row) for row in rows]

    def _utilization_in_period(
        self,
        employee_id: int,
        start: date,
        end: date,
        exclude_allocation_id: int | None = None,
    ) -> int:
        total = 0
        for row in self.allocations.list_active_for_employee(employee_id):
            if exclude_allocation_id and row.id == exclude_allocation_id:
                continue
            if _dates_overlap(row.alloc_start, row.alloc_end, start, end):
                total += row.utilization_percent
        return total

    def _refresh_employee_status(self, employee_id: int) -> None:
        employee = self.employees.get(employee_id)
        if employee is None:
            return
        has_active = bool(self.allocations.list_active_for_employee(employee_id))
        employee.status = (
            EmployeeStatus.ALLOCATED.value
            if has_active
            else EmployeeStatus.BENCH.value
        )
        self.employees.update(employee)

    def _get_manager_project(self, manager_user_id: int, project_id: int):
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError(f"No project with id {project_id}")
        if project.manager_user_id != manager_user_id:
            raise PermissionDeniedError("You can only manage your own projects")
        return project

    def _get_team_employee(self, manager_user_id: int, employee_id: int):
        employee = self.employees.get(employee_id)
        if employee is None:
            raise NotFoundError(f"No employee with id {employee_id}")
        if employee.manager_id != manager_user_id:
            raise PermissionDeniedError("You can only allocate employees on your team")
        if not employee.is_active:
            raise ValidationError("Employee is not active")
        return employee

    def list_team_employees(self, manager_user_id: int) -> list[dict]:
        rows = self.employees.list_by_manager(manager_user_id)
        result = []
        today = date.today()
        for employee in rows:
            util = self._utilization_in_period(
                employee.id, today, today
            )
            result.append(
                {
                    "id": employee.id,
                    "full_name": employee.full_name,
                    "department": employee.department,
                    "status": employee.status,
                    "current_utilization": util,
                }
            )
        return result

    def list_manager_projects(self, manager_user_id: int) -> list[dict]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "end_date": p.end_date,
            }
            for p in self.projects.list_by_manager(manager_user_id)
        ]

    def create_allocation(
        self,
        manager_user_id: int,
        project_id: int,
        employee_id: int,
        utilization_percent: int,
        alloc_start: date,
        alloc_end: date,
    ) -> dict:
        project = self._get_manager_project(manager_user_id, project_id)
        employee = self._get_team_employee(manager_user_id, employee_id)

        if project.status not in ALLOWED_PROJECT_STATUSES:
            raise ValidationError("Project must be PLANNED or ACTIVE")
        if alloc_start >= alloc_end:
            raise ValidationError("From date must be before to date")
        if utilization_percent <= 0 or utilization_percent > 100:
            raise ValidationError("Utilization must be between 1 and 100")

        current = self._utilization_in_period(employee.id, alloc_start, alloc_end)
        if current + utilization_percent > 100:
            raise ValidationError(
                f"Total utilization would be {current + utilization_percent}% "
                f"(max 100%) for the selected period"
            )

        row = self.allocations.add(
            Allocation(
                employee_id=employee.id,
                project_id=project.id,
                utilization_percent=utilization_percent,
                alloc_start=alloc_start,
                alloc_end=alloc_end,
                is_active=True,
            )
        )
        self._refresh_employee_status(employee.id)
        return self._allocation_row(row)

    def end_allocation(self, manager_user_id: int, allocation_id: int) -> dict:
        row = self.allocations.get(allocation_id)
        if row is None or not row.is_active:
            raise NotFoundError("Active allocation not found")
        project = self._get_manager_project(manager_user_id, row.project_id)

        today = date.today()
        row.is_active = False
        if row.alloc_end > today:
            row.alloc_end = today
        self.allocations.update(row)
        self._refresh_employee_status(row.employee_id)
        return self._allocation_row(row)
