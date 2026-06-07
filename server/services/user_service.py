from sqlalchemy.orm import Session

from server.core.enums import EmployeeStatus, Role
from server.core.exceptions import NotFoundError, ValidationError
from server.core.security import hash_password, password_strength_error
from server.models.employee import Employee
from server.models.user import User
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.user_repository import UserRepository

PROFILE_ROLES = {Role.MANAGER.value, Role.EMPLOYEE.value}


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.employees = EmployeeRepository(db)

    def create_user(
        self,
        full_name: str,
        email: str,
        username: str,
        temporary_password: str,
        role: str,
    ) -> User:
        if self.users.get_by_username(username):
            raise ValidationError("Username already exists")
        if self.users.get_by_email(email):
            raise ValidationError("Email already exists")
        strength_error = password_strength_error(temporary_password)
        if strength_error:
            raise ValidationError(strength_error)

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(temporary_password),
            role=role,
            is_active=True,
            force_password_change=True,
        )
        self.users.add(user)

        # V4: creating a MANAGER/EMPLOYEE auto-creates their employee profile (BENCH).
        if role in PROFILE_ROLES:
            self.employees.add(
                Employee(
                    user_id=user.id,
                    full_name=full_name,
                    email=email,
                    status=EmployeeStatus.BENCH.value,
                    is_active=True,
                )
            )
        return user

    def list_users(self) -> list[User]:
        return self.users.list()

    def _find_user(self, identifier: str) -> User:
        user = None
        if identifier.isdigit():
            user = self.users.get(int(identifier))
        if user is None:
            user = self.users.get_by_username(identifier)
        if user is None:
            raise NotFoundError(f"No user found for '{identifier}'")
        return user

    def reset_password(self, identifier: str, new_temporary_password: str) -> User:
        strength_error = password_strength_error(new_temporary_password)
        if strength_error:
            raise ValidationError(strength_error)
        user = self._find_user(identifier)
        user.password_hash = hash_password(new_temporary_password)
        user.force_password_change = True
        return self.users.update(user)

    def set_active(self, identifier: str, is_active: bool) -> User:
        user = self._find_user(identifier)
        user.is_active = is_active
        self.users.update(user)
        profile = self.employees.get_by_user_id(user.id)
        if profile is not None:
            profile.is_active = is_active
            self.employees.update(profile)
        return user
