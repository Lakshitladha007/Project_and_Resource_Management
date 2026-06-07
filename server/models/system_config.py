from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from server.db.database import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    llm_provider: Mapped[str] = mapped_column(String(20), default="GEMINI", nullable=False)
    llm_api_key_encrypted: Mapped[str] = mapped_column(
        String(512), default="", nullable=False
    )
    scheduler_interval_hours: Mapped[int] = mapped_column(
        Integer, default=6, nullable=False
    )
    max_weekly_hours: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
