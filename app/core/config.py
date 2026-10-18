from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    app_name: str = "OtimizaPL"

    api_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+psycopg://"
        "tcc:tcc@localhost:5432/tcc_otimizador"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()