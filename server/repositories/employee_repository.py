from sqlalchemy.orm import Session

from server.models.employee import Employee
from server.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: Session):
        super().__init__(Employee, db)

    def get_by_user_id(self, user_id: int) -> Employee | None:
        return self.db.query(Employee).filter(Employee.user_id == user_id).first()

    def list_by_manager(self, manager_user_id: int) -> list[Employee]:
        return (
            self.db.query(Employee)
            .filter(
                Employee.manager_id == manager_user_id,
                Employee.is_active.is_(True),
            )
            .all()
        )
