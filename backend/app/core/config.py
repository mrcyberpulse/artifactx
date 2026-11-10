from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from ARTIFACTX_* environment variables. No secrets live in code."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_prefix="ARTIFACTX_", extra="ignore"
    )

    app_name: str = "ArtifactX"
    edition: str = "Community Edition"
    version: str = "1.0.0"
    brand: str = "MR CYBER"
    creator: str = "Harsh Saini"
    environment: str = "development"  # development | testing | production
    docs_enabled: bool = True

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    secret_key: SecretStr
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    password_reset_minutes: int = 30
    cookie_secure: bool = True
    registration_enabled: bool = True

    # Comma-separated list of allowed browser origins. Same-origin deployments need none.
    cors_origins: str = ""
    frontend_url: str = "http://localhost:5173"

    rate_limit_enabled: bool = True

    @field_validator("secret_key")
    @classmethod
    def _secret_long_enough(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("ARTIFACTX_SECRET_KEY must be at least 32 characters.")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
