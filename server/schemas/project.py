from datetime import date

from pydantic import BaseModel, Field

from server.core.enums import ProjectStatus


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""
    start_date: date
    end_date: date
    status: ProjectStatus
    manager_user_id: int
    total_story_points: int = Field(ge=0)


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: ProjectStatus | None = None
    manager_user_id: int | None = None
    total_story_points: int | None = Field(default=None, ge=0)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    status: str
    manager_user_id: int
    manager_name: str
    total_story_points: int
    story_points_done: int
    health_status: str

    model_config = {"from_attributes": True}
