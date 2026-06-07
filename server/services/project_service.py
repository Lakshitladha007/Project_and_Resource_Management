from datetime import date

from sqlalchemy.orm import Session

from server.core.enums import HealthStatus, Role
from server.core.exceptions import NotFoundError, ValidationError
from server.models.project import Project
from server.repositories.employee_repository import EmployeeRepository
from server.repositories.project_repository import ProjectRepository
from server.repositories.user_repository import UserRepository


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.users = UserRepository(db)
        self.employees = EmployeeRepository(db)

    def _manager_name(self, manager_user_id: int) -> str:
        user = self.users.get(manager_user_id)
        if user is None:
            return str(manager_user_id)
        profile = self.employees.get_by_user_id(manager_user_id)
        if profile is not None:
            return profile.full_name
        return user.username

    def _validate_manager(self, manager_user_id: int) -> None:
        manager = self.users.get(manager_user_id)
        if manager is None or manager.role != Role.MANAGER.value:
            raise ValidationError("Manager User ID must reference a MANAGER account")

    def _validate_dates(self, start_date: date, end_date: date) -> None:
        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")

    def _to_response(self, project: Project) -> dict:
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "status": project.status,
            "manager_user_id": project.manager_user_id,
            "manager_name": self._manager_name(project.manager_user_id),
            "total_story_points": project.total_story_points,
            "story_points_done": 0,
            "health_status": project.health_status,
        }

    def create_project(
        self,
        name: str,
        description: str,
        start_date: date,
        end_date: date,
        status: str,
        manager_user_id: int,
        total_story_points: int,
    ) -> dict:
        if self.projects.get_by_name(name.strip()):
            raise ValidationError("Project name already exists")
        self._validate_manager(manager_user_id)
        self._validate_dates(start_date, end_date)
        if total_story_points < 0:
            raise ValidationError("Total story points cannot be negative")

        project = self.projects.add(
            Project(
                name=name.strip(),
                description=description.strip(),
                start_date=start_date,
                end_date=end_date,
                status=status,
                manager_user_id=manager_user_id,
                total_story_points=total_story_points,
                health_status=HealthStatus.ON_TRACK.value,
            )
        )
        return self._to_response(project)

    def list_projects(self) -> list[dict]:
        return [self._to_response(p) for p in self.projects.list()]

    def update_project(
        self,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        manager_user_id: int | None = None,
        total_story_points: int | None = None,
    ) -> dict:
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError(f"No project with id {project_id}")

        if name is not None:
            trimmed = name.strip()
            existing = self.projects.get_by_name(trimmed)
            if existing is not None and existing.id != project.id:
                raise ValidationError("Project name already exists")
            project.name = trimmed
        if description is not None:
            project.description = description.strip()
        if start_date is not None:
            project.start_date = start_date
        if end_date is not None:
            project.end_date = end_date
        if status is not None:
            project.status = status
        if manager_user_id is not None:
            self._validate_manager(manager_user_id)
            project.manager_user_id = manager_user_id
        if total_story_points is not None:
            if total_story_points < 0:
                raise ValidationError("Total story points cannot be negative")
            project.total_story_points = total_story_points

        self._validate_dates(project.start_date, project.end_date)
        self.projects.update(project)
        return self._to_response(project)
