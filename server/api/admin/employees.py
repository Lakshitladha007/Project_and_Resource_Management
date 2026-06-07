from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.employee import (
    AssignManagerRequest,
    EmployeeResponse,
    UpdateEmployeeRequest,
)
from server.schemas.skill import (
    AddEmployeeSkillRequest,
    EmployeeSkillResponse,
    UpdateProficiencyRequest,
)
from server.services.employee_service import EmployeeService
from server.services.skill_service import SkillService

router = APIRouter(prefix="/admin/employees", tags=["admin-employees"])

admin_only = require_role(Role.ADMIN.value)


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[EmployeeResponse]:
    return [
        EmployeeResponse.model_validate(e)
        for e in EmployeeService(db).list_employees()
    ]


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: UpdateEmployeeRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> EmployeeResponse:
    employee = EmployeeService(db).update_employee(
        employee_id,
        full_name=payload.full_name,
        department=payload.department,
        designation=payload.designation,
    )
    return EmployeeResponse.model_validate(employee)


@router.post("/assign-manager", response_model=EmployeeResponse)
def assign_manager(
    payload: AssignManagerRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> EmployeeResponse:
    employee = EmployeeService(db).assign_manager(
        payload.employee_user_id, payload.manager_user_id
    )
    return EmployeeResponse.model_validate(employee)


@router.post("/{employee_id}/deactivate")
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> dict:
    EmployeeService(db).deactivate_employee(employee_id)
    return {"detail": "Employee deactivated."}


@router.get("/{employee_id}/skills", response_model=list[EmployeeSkillResponse])
def list_employee_skills(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[EmployeeSkillResponse]:
    return [
        EmployeeSkillResponse(**row)
        for row in SkillService(db).list_employee_skills(employee_id)
    ]


@router.post("/{employee_id}/skills", response_model=EmployeeSkillResponse)
def add_employee_skill(
    employee_id: int,
    payload: AddEmployeeSkillRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> EmployeeSkillResponse:
    row = SkillService(db).add_skill(
        employee_id,
        payload.skill_name,
        payload.category.value,
        payload.proficiency.value,
    )
    return EmployeeSkillResponse(**row)


@router.put(
    "/{employee_id}/skills/{employee_skill_id}",
    response_model=EmployeeSkillResponse,
)
def update_employee_skill(
    employee_id: int,
    employee_skill_id: int,
    payload: UpdateProficiencyRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> EmployeeSkillResponse:
    row = SkillService(db).update_proficiency(
        employee_id, employee_skill_id, payload.proficiency.value
    )
    return EmployeeSkillResponse(**row)


@router.delete("/{employee_id}/skills/{employee_skill_id}")
def remove_employee_skill(
    employee_id: int,
    employee_skill_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> dict:
    SkillService(db).remove_skill(employee_id, employee_skill_id)
    return {"detail": "Skill removed."}
