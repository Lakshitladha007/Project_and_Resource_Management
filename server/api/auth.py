from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.dependencies import get_current_user, get_db
from server.models.user import User
from server.schemas.auth import ChangePasswordRequest, LoginRequest, TokenResponse
from server.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user, token = AuthService(db).login(payload.username, payload.password)
    return TokenResponse(
        access_token=token,
        role=user.role,
        force_password_change=user.force_password_change,
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    AuthService(db).change_password(
        current_user, payload.current_password, payload.new_password
    )
    return {"detail": "Password changed successfully"}
