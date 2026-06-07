from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.allocation import (
    AllocationResponse,
    CreateAllocationRequest,
    ManagerProjectResponse,
    TeamEmployeeResponse,
)
from server.services.allocation_service import AllocationService

router = APIRouter(prefix="/manager", tags=["manager"])

manager_only = require_role(Role.MANAGER.value)


@router.get("/employees", response_model=list[TeamEmployeeResponse])
def list_team_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> list[TeamEmployeeResponse]:
    rows = AllocationService(db).list_team_employees(current_user.id)
    return [TeamEmployeeResponse(**row) for row in rows]


@router.get("/projects", response_model=list[ManagerProjectResponse])
def list_manager_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> list[ManagerProjectResponse]:
    rows = AllocationService(db).list_manager_projects(current_user.id)
    return [ManagerProjectResponse(**row) for row in rows]


@router.get(
    "/projects/{project_id}/allocations",
    response_model=list[AllocationResponse],
)
def list_project_allocations(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> list[AllocationResponse]:
    service = AllocationService(db)
    service._get_manager_project(current_user.id, project_id)
    rows = service.list_allocations(project_id=project_id)
    return [AllocationResponse(**row) for row in rows]


@router.post("/allocations", response_model=AllocationResponse)
def create_allocation(
    payload: CreateAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> AllocationResponse:
    row = AllocationService(db).create_allocation(
        current_user.id,
        payload.project_id,
        payload.employee_id,
        payload.utilization_percent,
        payload.alloc_start,
        payload.alloc_end,
    )
    return AllocationResponse(**row)


@router.post("/allocations/{allocation_id}/end", response_model=AllocationResponse)
def end_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_only),
) -> AllocationResponse:
    row = AllocationService(db).end_allocation(current_user.id, allocation_id)
    return AllocationResponse(**row)
