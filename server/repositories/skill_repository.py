from sqlalchemy.orm import Session

from server.models.skill import Skill
from server.repositories.base_repository import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, db: Session):
        super().__init__(Skill, db)

    def get_by_name(self, name: str) -> Skill | None:
        return self.db.query(Skill).filter(Skill.name == name).first()
