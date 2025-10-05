from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Bible Verse of the Day"
    timezone: str = "UTC"
    database_url: str = Field(default="sqlite:///./bible.db")
    seed: int | None = None

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()
