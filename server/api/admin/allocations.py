from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.allocation import AllocationResponse
from server.services.allocation_service import AllocationService

router = APIRouter(prefix="/admin/allocations", tags=["admin-allocations"])

admin_only = require_role(Role.ADMIN.value)


@router.get("", response_model=list[AllocationResponse])
def list_allocations(
    employee_id: int | None = Query(default=None),
    project_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[AllocationResponse]:
    rows = AllocationService(db).list_allocations(
        employee_id=employee_id, project_id=project_id
    )
    return [AllocationResponse(**row) for row in rows]
