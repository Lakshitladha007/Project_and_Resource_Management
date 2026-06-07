from sqlalchemy.orm import Session

from server.repositories.allocation_repository import AllocationRepository
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.project_repository import ProjectRepository


class AllocationService:
    def __init__(self, db: Session):
        self.db = db
        self.allocations = AllocationRepository(db)
        self.employees = EmployeeRepository(db)
        self.projects = ProjectRepository(db)

    def list_allocations(
        self,
        employee_id: int | None = None,
        project_id: int | None = None,
    ) -> list[dict]:
        rows = self.allocations.list_active(
            employee_id=employee_id, project_id=project_id
        )
        result = []
        for row in rows:
            employee = self.employees.get(row.employee_id)
            project = self.projects.get(row.project_id)
            result.append(
                {
                    "id": row.id,
                    "employee_id": row.employee_id,
                    "employee_name": employee.full_name if employee else str(row.employee_id),
                    "project_id": row.project_id,
                    "project_name": project.name if project else str(row.project_id),
                    "utilization_percent": row.utilization_percent,
                    "alloc_start": row.alloc_start,
                    "alloc_end": row.alloc_end,
                }
            )
        return result
