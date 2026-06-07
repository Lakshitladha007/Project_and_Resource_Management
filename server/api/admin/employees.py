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
from server.services.employee_service import EmployeeService

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
