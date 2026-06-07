from sqlalchemy.orm import Session

from server.core.enums import Role
from server.core.exceptions import NotFoundError, ValidationError
from server.models.employee import Employee
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.user_repository import UserRepository


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.employees = EmployeeRepository(db)
        self.users = UserRepository(db)

    def list_employees(self) -> list[Employee]:
        return self.employees.list()

    def _get_or_404(self, employee_id: int) -> Employee:
        employee = self.employees.get(employee_id)
        if employee is None:
            raise NotFoundError(f"No employee with id {employee_id}")
        return employee

    def update_employee(
        self,
        employee_id: int,
        full_name: str | None = None,
        department: str | None = None,
        designation: str | None = None,
    ) -> Employee:
        employee = self._get_or_404(employee_id)
        if full_name is not None:
            employee.full_name = full_name
        if department is not None:
            employee.department = department
        if designation is not None:
            employee.designation = designation
        return self.employees.update(employee)

    def assign_manager(self, employee_user_id: int, manager_user_id: int) -> Employee:
        employee = self.employees.get_by_user_id(employee_user_id)
        if employee is None:
            raise NotFoundError(
                f"No employee linked to user id {employee_user_id}"
            )
        if employee_user_id == manager_user_id:
            raise ValidationError("An employee cannot be their own manager")
        manager = self.users.get(manager_user_id)
        if manager is None or manager.role != Role.MANAGER.value:
            raise ValidationError("Manager User ID must reference a MANAGER account")
        employee.manager_id = manager_user_id
        return self.employees.update(employee)

    def deactivate_employee(self, employee_id: int) -> Employee:
        employee = self._get_or_404(employee_id)
        employee.is_active = False
        self.employees.update(employee)
        user = self.users.get(employee.user_id)
        if user is not None:
            user.is_active = False
            self.users.update(user)
        return employee
