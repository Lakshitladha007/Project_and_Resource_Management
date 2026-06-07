from server.config import settings
from server.core.enums import Role
from server.core.security import hash_password
from server.db.database import SessionLocal
from server.models.system_config import SystemConfig
from server.models.user import User

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@1234"
DEFAULT_ADMIN_EMAIL = "admin@prm.local"


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first():
            print("Admin already exists; skipping admin creation.")
        else:
            db.add(
                User(
                    username=DEFAULT_ADMIN_USERNAME,
                    email=DEFAULT_ADMIN_EMAIL,
                    password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                    role=Role.ADMIN.value,
                    is_active=True,
                    force_password_change=True,
                )
            )
            print(
                f"Created first admin '{DEFAULT_ADMIN_USERNAME}' "
                f"(password '{DEFAULT_ADMIN_PASSWORD}', must change on first login)."
            )

        if db.query(SystemConfig).first() is None:
            db.add(
                SystemConfig(
                    llm_provider=settings.llm_provider,
                    scheduler_interval_hours=settings.scheduler_interval_hours,
                    max_weekly_hours=settings.max_weekly_hours,
                )
            )
            print("Created default system config row.")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
