from typing import Callable, Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from server.core.exceptions import AuthenticationError, PermissionDeniedError
from server.core.security import decode_access_token
from server.db.database import SessionLocal
from server.models.user import User
from server.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise AuthenticationError(str(exc))
    username = payload.get("sub")
    user = UserRepository(db).get_by_username(username)
    if user is None:
        raise AuthenticationError("User not found")
    return user


def require_role(*roles: str) -> Callable[..., User]:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise PermissionDeniedError(
                "You do not have permission to perform this action"
            )
        return current_user

    return checker
