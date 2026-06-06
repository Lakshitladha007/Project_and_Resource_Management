from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    force_password_change: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
