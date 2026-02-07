"""Application configuration using pydantic-settings."""

from pydantic import model_validator
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

    # Zitadel (OIDC)
    # Self-hosted base URL, e.g. https://zitadel.example.com
    ZITADEL_BASE_URL: str = ""
    # OIDC issuer. If empty, defaults to ZITADEL_BASE_URL.
    ZITADEL_ISSUER: str = ""
    # Expected audience for access tokens (your API / project audience)
    ZITADEL_AUDIENCE: str = ""
    # JWKS cache TTL
    ZITADEL_JWKS_CACHE_TTL_SECONDS: int = 3600
    # Clock skew leeway in seconds for exp/nbf checks
    ZITADEL_CLOCK_SKEW_SECONDS: int = 10
    # Introspection client auth (client_secret_basic)
    ZITADEL_INTROSPECTION_CLIENT_ID: str = ""
    ZITADEL_INTROSPECTION_CLIENT_SECRET: str = ""
    # User mapping behavior
    ZITADEL_USER_AUTOCREATE: bool = True

    # Dev: allow test user without Zitadel (Bearer dev:<email> or dev:<email>:<name>)
    # Only use when Zitadel is not configured. Never enable in production.
    DEV_TEST_USER_ENABLED: bool = False

    # Observability (optional)
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SERVICE_NAME: str = "mitlist"

    @model_validator(mode="after")
    def validate_security_flags(self) -> "Settings":
        """Ensure secure configuration in production."""
        if self.is_production and self.DEV_TEST_USER_ENABLED:
            raise ValueError("DEV_TEST_USER_ENABLED cannot be True in production environment")
        return self

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct async PostgreSQL connection URI."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    @property
    def zitadel_discovery_url(self) -> str:
        """OIDC discovery endpoint."""
        base = self.ZITADEL_BASE_URL.rstrip("/")
        return f"{base}/.well-known/openid-configuration" if base else ""

    @property
    def zitadel_introspection_url(self) -> str:
        """OAuth introspection endpoint."""
        base = self.ZITADEL_BASE_URL.rstrip("/")
        return f"{base}/oauth/v2/introspect" if base else ""

    @property
    def zitadel_issuer(self) -> str:
        """Expected issuer for tokens."""
        return (self.ZITADEL_ISSUER or self.ZITADEL_BASE_URL).rstrip("/")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ("local", "development", "dev")


settings = Settings()
