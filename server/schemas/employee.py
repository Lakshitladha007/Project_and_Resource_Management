from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    department: str | None
    designation: str | None
    status: str
    manager_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}


class UpdateEmployeeRequest(BaseModel):
    full_name: str | None = None
    department: str | None = None
    designation: str | None = None


class AssignManagerRequest(BaseModel):
    employee_user_id: int
    manager_user_id: int
