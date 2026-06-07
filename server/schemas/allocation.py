from datetime import date

from pydantic import BaseModel


class AllocationResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    project_id: int
    project_name: str
    utilization_percent: int
    alloc_start: date
    alloc_end: date
