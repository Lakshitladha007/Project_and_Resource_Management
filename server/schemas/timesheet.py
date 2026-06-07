from datetime import date

from pydantic import BaseModel, Field


class ActivityTagResponse(BaseModel):
    id: int
    label: str
    display_order: int


class TimesheetReminderResponse(BaseModel):
    show_reminder: bool
    week_start: date


class TimesheetProjectPreview(BaseModel):
    project_id: int
    project_name: str
    utilization_percent: int
    max_hours: int


class TimesheetPreviewResponse(BaseModel):
    employee_name: str
    week_start: date
    max_weekly_hours: int
    projects: list[TimesheetProjectPreview]


class EntryTagRequest(BaseModel):
    activity_tag_id: int | None = None
    custom_label: str | None = None


class TimesheetEntryRequest(BaseModel):
    project_id: int
    hours: int = Field(ge=0)
    tags: list[EntryTagRequest] = Field(default_factory=list)


class SubmitTimesheetRequest(BaseModel):
    week_start: date
    entries: list[TimesheetEntryRequest]


class TimesheetSummaryResponse(BaseModel):
    week_start: date
    total_hours: int
    status: str


class TimesheetEntryDetailResponse(BaseModel):
    project_id: int
    project_name: str
    hours: int
    activity_tags: list[str]


class TimesheetDetailResponse(BaseModel):
    week_start: date
    total_hours: int
    status: str
    entries: list[TimesheetEntryDetailResponse]


class EmployeeAllocationResponse(BaseModel):
    project_name: str
    utilization_percent: int
    alloc_start: date
    alloc_end: date
    status: str


class EmployeeAllocationsListResponse(BaseModel):
    allocations: list[EmployeeAllocationResponse]
    total_utilization: int
