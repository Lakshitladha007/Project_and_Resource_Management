from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from server.db.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
