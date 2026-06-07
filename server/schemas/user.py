from pydantic import BaseModel

from server.core.enums import Role


class CreateUserRequest(BaseModel):
    full_name: str
    email: str
    username: str
    temporary_password: str
    role: Role


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class ResetPasswordRequest(BaseModel):
    new_temporary_password: str
