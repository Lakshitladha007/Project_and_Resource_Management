from sqlalchemy.orm import Session

from server.core.enums import MilestoneStatus
from server.models.milestone import Milestone
from server.repositories.base_repository import BaseRepository


class MilestoneRepository(BaseRepository[Milestone]):
    def __init__(self, db: Session):
        super().__init__(Milestone, db)

    def list_for_project(self, project_id: int) -> list[Milestone]:
        return (
            self.db.query(Milestone)
            .filter(Milestone.project_id == project_id)
            .order_by(Milestone.due_date)
            .all()
        )

    def sum_done_points(self, project_id: int) -> int:
        rows = (
            self.db.query(Milestone)
            .filter(
                Milestone.project_id == project_id,
                Milestone.status == MilestoneStatus.DONE.value,
            )
            .all()
        )
        return sum(row.story_points for row in rows)

    def get_for_project(self, project_id: int, milestone_id: int) -> Milestone | None:
        return (
            self.db.query(Milestone)
            .filter(
                Milestone.id == milestone_id,
                Milestone.project_id == project_id,
            )
            .first()
        )
