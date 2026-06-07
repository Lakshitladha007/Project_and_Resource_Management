from datetime import date

from pydantic import BaseModel, Field

from server.core.enums import MilestoneStatus


class MilestoneResponse(BaseModel):
    id: int
    title: str
    due_date: date
    story_points: int
    status: str


class MilestoneListResponse(BaseModel):
    project_id: int
    project_name: str
    milestones: list[MilestoneResponse]
    total_story_points: int
    completed_story_points: int
    remaining_story_points: int


class CreateMilestoneRequest(BaseModel):
    title: str
    due_date: date
    story_points: int = Field(ge=0)


class UpdateMilestoneStatusRequest(BaseModel):
    status: MilestoneStatus
