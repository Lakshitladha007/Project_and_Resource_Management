from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.core.enums import Role
from server.dependencies import get_db, require_role
from server.models.user import User
from server.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
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
