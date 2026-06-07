from datetime import date

from pydantic import BaseModel, Field


class AllocationResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    project_id: int
    project_name: str
    utilization_percent: int
    alloc_start: date
    alloc_end: date


class CreateAllocationRequest(BaseModel):
    project_id: int
    employee_id: int
    utilization_percent: int = Field(ge=1, le=100)
    alloc_start: date
    alloc_end: date


class TeamEmployeeResponse(BaseModel):
    id: int
    full_name: str
    department: str | None
    status: str
    current_utilization: int


class ManagerProjectResponse(BaseModel):
    id: int
    name: str
    status: str
    end_date: date
