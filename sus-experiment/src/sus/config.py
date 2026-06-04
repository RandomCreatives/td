from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Telegram API Credentials
    api_id: int
    api_hash: str
    phone_number: str

    # Database Configuration
    postgres_user: str = "sus_researcher"
    postgres_password: str = "password"
    postgres_db: str = "sus_research"
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379

    # Experiment Configuration
    overlap_threshold: int = 3
    cycle_hour: int = 21
    expiry_hours: int = 48
    salt_rotation_days: int = 7

    # Security
    sus_frozen: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
