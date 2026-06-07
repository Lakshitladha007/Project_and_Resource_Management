from sqlalchemy.orm import Session

from server.models.user import User
from server.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
