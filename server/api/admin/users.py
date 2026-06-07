from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.user import CreateUserRequest, ResetPasswordRequest, UserResponse
from server.services.user_service import UserService

router = APIRouter(prefix="/admin/users", tags=["admin-users"])

admin_only = require_role(Role.ADMIN.value)


@router.post("", response_model=UserResponse)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> UserResponse:
    user = UserService(db).create_user(
        full_name=payload.full_name,
        email=payload.email,
        username=payload.username,
        temporary_password=payload.temporary_password,
        role=payload.role.value,
    )
    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[UserResponse]:
    return [UserResponse.model_validate(u) for u in UserService(db).list_users()]


@router.post("/{identifier}/reset-password")
def reset_password(
    identifier: str,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> dict:
    UserService(db).reset_password(identifier, payload.new_temporary_password)
    return {"detail": "Password reset. User must change it on next login."}


@router.post("/{identifier}/deactivate")
def deactivate_user(
    identifier: str,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> dict:
    UserService(db).set_active(identifier, False)
    return {"detail": "User deactivated."}


@router.post("/{identifier}/reactivate")
def reactivate_user(
    identifier: str,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> dict:
    UserService(db).set_active(identifier, True)
    return {"detail": "User reactivated."}
