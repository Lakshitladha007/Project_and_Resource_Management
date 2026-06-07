from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.milestone import (
    CreateMilestoneRequest,
    MilestoneListResponse,
    MilestoneResponse,
    UpdateMilestoneStatusRequest,
)
from server.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
from server.services.milestone_service import MilestoneService
from server.services.project_service import ProjectService

router = APIRouter(prefix="/admin/projects", tags=["admin-projects"])

admin_only = require_role(Role.ADMIN.value)


@router.post("", response_model=ProjectResponse)
def create_project(
    payload: CreateProjectRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> ProjectResponse:
    row = ProjectService(db).create_project(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status.value,
        manager_user_id=payload.manager_user_id,
        total_story_points=payload.total_story_points,
    )
    return ProjectResponse(**row)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> list[ProjectResponse]:
    return [ProjectResponse(**row) for row in ProjectService(db).list_projects()]


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: UpdateProjectRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> ProjectResponse:
    row = ProjectService(db).update_project(
        project_id,
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=payload.status.value if payload.status else None,
        manager_user_id=payload.manager_user_id,
        total_story_points=payload.total_story_points,
    )
    return ProjectResponse(**row)


@router.get("/{project_id}/milestones", response_model=MilestoneListResponse)
def list_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> MilestoneListResponse:
    return MilestoneListResponse(**MilestoneService(db).list_milestones(project_id))


@router.post("/{project_id}/milestones", response_model=MilestoneResponse)
def add_milestone(
    project_id: int,
    payload: CreateMilestoneRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> MilestoneResponse:
    row = MilestoneService(db).add_milestone(
        project_id, payload.title, payload.due_date, payload.story_points
    )
    return MilestoneResponse(**row)


@router.put(
    "/{project_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
)
def update_milestone_status(
    project_id: int,
    milestone_id: int,
    payload: UpdateMilestoneStatusRequest,
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> MilestoneResponse:
    row = MilestoneService(db).update_status(
        project_id, milestone_id, payload.status.value
    )
    return MilestoneResponse(**row)
