from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from server.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository (Repository pattern)."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, entity_id: int) -> ModelType | None:
        return self.db.get(self.model, entity_id)

    def list(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def add(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)
        self.db.commit()
