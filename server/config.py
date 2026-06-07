from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://root:root@localhost:3306/prm"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    max_weekly_hours: int = 40
    llm_provider: str = "GEMINI"
    gemini_api_key: str = ""
    scheduler_interval_hours: int = 6


settings = Settings()
