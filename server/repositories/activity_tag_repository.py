from datetime import date

from sqlalchemy.orm import Session

from server.models.timesheet import ActivityTag
from server.repositories.base_repository import BaseRepository


class ActivityTagRepository(BaseRepository[ActivityTag]):
    def __init__(self, db: Session):
        super().__init__(ActivityTag, db)

    def list_ordered(self) -> list[ActivityTag]:
        return (
            self.db.query(ActivityTag).order_by(ActivityTag.display_order).all()
        )
