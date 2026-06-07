from sqlalchemy.orm import Session

from server.models.skill import EmployeeSkill
from server.repositories.base_repository import BaseRepository


class EmployeeSkillRepository(BaseRepository[EmployeeSkill]):
    def __init__(self, db: Session):
        super().__init__(EmployeeSkill, db)

    def list_for_employee(self, employee_id: int) -> list[EmployeeSkill]:
        return (
            self.db.query(EmployeeSkill)
            .filter(EmployeeSkill.employee_id == employee_id)
            .all()
        )

    def get_for_employee(self, employee_id: int, employee_skill_id: int) -> EmployeeSkill | None:
        return (
            self.db.query(EmployeeSkill)
            .filter(
                EmployeeSkill.id == employee_skill_id,
                EmployeeSkill.employee_id == employee_id,
            )
            .first()
        )

    def get_by_employee_and_skill(
        self, employee_id: int, skill_id: int
    ) -> EmployeeSkill | None:
        return (
            self.db.query(EmployeeSkill)
            .filter(
                EmployeeSkill.employee_id == employee_id,
                EmployeeSkill.skill_id == skill_id,
            )
            .first()
        )
