from sqlalchemy.orm import Session

from server.models.project import Project
from server.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_name(self, name: str) -> Project | None:
        return self.db.query(Project).filter(Project.name == name).first()
