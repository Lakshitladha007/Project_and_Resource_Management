from pydantic import BaseModel

from server.core.enums import ProficiencyLevel, SkillCategory


class EmployeeSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    category: str
    proficiency: str


class AddEmployeeSkillRequest(BaseModel):
    skill_name: str
    category: SkillCategory
    proficiency: ProficiencyLevel


class UpdateProficiencyRequest(BaseModel):
    proficiency: ProficiencyLevel
