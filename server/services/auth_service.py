from sqlalchemy.orm import Session

from server.core.exceptions import AuthenticationError, ValidationError
from server.core.security import (
    create_access_token,
    hash_password,
    password_strength_error,
    verify_password,
)
from server.models.user import User
from server.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def login(self, username: str, password: str) -> tuple[User, str]:
        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        token = create_access_token(subject=user.username, role=user.role)
        return user, token

    def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> User:
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        strength_error = password_strength_error(new_password)
        if strength_error:
            raise ValidationError(strength_error)
        if new_password == current_password:
            raise ValidationError("New password must differ from the current one")
        user.password_hash = hash_password(new_password)
        user.force_password_change = False
        self.users.update(user)
        return user
