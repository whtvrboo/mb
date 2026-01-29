"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Project
    PROJECT_NAME: str = "mitlist"
    ENVIRONMENT: str = "local"

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Security
    SECRET_KEY: str

    # Observability (optional)
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SERVICE_NAME: str = "mitlist"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct async PostgreSQL connection URI."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ("local", "development", "dev")


settings = Settings()
