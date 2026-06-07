from sqlalchemy.orm import Session

from server.core.exceptions import NotFoundError, ValidationError
from server.models.skill import EmployeeSkill, Skill
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.employee_skill_repository import EmployeeSkillRepository
from server.repositories.skill_repository import SkillRepository


class SkillService:
    def __init__(self, db: Session):
        self.db = db
        self.employees = EmployeeRepository(db)
        self.skills = SkillRepository(db)
        self.employee_skills = EmployeeSkillRepository(db)

    def _get_employee_or_404(self, employee_id: int):
        employee = self.employees.get(employee_id)
        if employee is None:
            raise NotFoundError(f"No employee with id {employee_id}")
        return employee

    def list_employee_skills(self, employee_id: int) -> list[dict]:
        self._get_employee_or_404(employee_id)
        rows = self.employee_skills.list_for_employee(employee_id)
        result = []
        for row in rows:
            skill = self.skills.get(row.skill_id)
            if skill is None:
                continue
            result.append(
                {
                    "id": row.id,
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "category": skill.category,
                    "proficiency": row.proficiency,
                }
            )
        return result

    def _get_or_create_skill(self, name: str, category: str) -> Skill:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("Skill name cannot be empty")
        existing = self.skills.get_by_name(normalized)
        if existing is not None:
            if existing.category != category:
                raise ValidationError(
                    f"Skill '{normalized}' already exists under category {existing.category}"
                )
            return existing
        return self.skills.add(Skill(name=normalized, category=category))

    def add_skill(
        self, employee_id: int, skill_name: str, category: str, proficiency: str
    ) -> dict:
        self._get_employee_or_404(employee_id)
        skill = self._get_or_create_skill(skill_name, category)
        if self.employee_skills.get_by_employee_and_skill(employee_id, skill.id):
            raise ValidationError(f"Employee already has skill '{skill.name}'")
        row = self.employee_skills.add(
            EmployeeSkill(
                employee_id=employee_id,
                skill_id=skill.id,
                proficiency=proficiency,
            )
        )
        return {
            "id": row.id,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "category": skill.category,
            "proficiency": row.proficiency,
        }

    def update_proficiency(
        self, employee_id: int, employee_skill_id: int, proficiency: str
    ) -> dict:
        self._get_employee_or_404(employee_id)
        row = self.employee_skills.get_for_employee(employee_id, employee_skill_id)
        if row is None:
            raise NotFoundError("Skill assignment not found for this employee")
        row.proficiency = proficiency
        self.employee_skills.update(row)
        skill = self.skills.get(row.skill_id)
        return {
            "id": row.id,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "category": skill.category,
            "proficiency": row.proficiency,
        }

    def remove_skill(self, employee_id: int, employee_skill_id: int) -> None:
        self._get_employee_or_404(employee_id)
        row = self.employee_skills.get_for_employee(employee_id, employee_skill_id)
        if row is None:
            raise NotFoundError("Skill assignment not found for this employee")
        self.employee_skills.delete(row)
