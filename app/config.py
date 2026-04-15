from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    serpapi_api_key: str = Field(alias="SERPAPI_API_KEY")
    db_connection: str = Field(alias="DB_CONNECTION")


@lru_cache
def get_settings() -> Settings:
    return Settings()
