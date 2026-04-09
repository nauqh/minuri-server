from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    serpapi_api_key: str = os.getenv("SERPAPI_API_KEY")
    cors_origins: list[str] = ["http://localhost:5173"]
    default_limit: int = 10
    max_limit: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
