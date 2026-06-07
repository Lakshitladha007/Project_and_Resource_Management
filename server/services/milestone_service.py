from datetime import date

from sqlalchemy.orm import Session

from server.core.enums import MilestoneStatus
from server.core.exceptions import NotFoundError, ValidationError
from server.models.milestone import Milestone
from server.repositories.milestone_repository import MilestoneRepository
from server.repositories.project_repository import ProjectRepository


class MilestoneService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.milestones = MilestoneRepository(db)

    def _get_project_or_404(self, project_id: int):
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError(f"No project with id {project_id}")
        return project

    def _milestone_row(self, milestone: Milestone) -> dict:
        return {
            "id": milestone.id,
            "title": milestone.title,
            "due_date": milestone.due_date,
            "story_points": milestone.story_points,
            "status": milestone.status,
        }

    def list_milestones(self, project_id: int) -> dict:
        project = self._get_project_or_404(project_id)
        rows = self.milestones.list_for_project(project_id)
        completed = self.milestones.sum_done_points(project_id)
        return {
            "project_id": project.id,
            "project_name": project.name,
            "milestones": [self._milestone_row(m) for m in rows],
            "total_story_points": project.total_story_points,
            "completed_story_points": completed,
            "remaining_story_points": max(project.total_story_points - completed, 0),
        }

    def add_milestone(
        self, project_id: int, title: str, due_date: date, story_points: int
    ) -> dict:
        self._get_project_or_404(project_id)
        trimmed = title.strip()
        if not trimmed:
            raise ValidationError("Milestone title cannot be empty")
        if story_points < 0:
            raise ValidationError("Story points cannot be negative")
        milestone = self.milestones.add(
            Milestone(
                project_id=project_id,
                title=trimmed,
                due_date=due_date,
                story_points=story_points,
                status=MilestoneStatus.NOT_STARTED.value,
            )
        )
        return self._milestone_row(milestone)

    def update_status(
        self, project_id: int, milestone_id: int, status: str
    ) -> dict:
        self._get_project_or_404(project_id)
        milestone = self.milestones.get_for_project(project_id, milestone_id)
        if milestone is None:
            raise NotFoundError("Milestone not found for this project")
        milestone.status = status
        self.milestones.update(milestone)
        return self._milestone_row(milestone)
