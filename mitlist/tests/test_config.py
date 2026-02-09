import pytest
from pydantic import ValidationError
from mitlist.core.config import Settings

def test_settings_production_dev_user_enabled_error():
    """Ensure DEV_TEST_USER_ENABLED cannot be True in production."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(
            ENVIRONMENT="production",
            DEV_TEST_USER_ENABLED=True,
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="password",
            POSTGRES_DB="db",
            SECRET_KEY="secret"
        )
    assert "DEV_TEST_USER_ENABLED must be False in production environment." in str(excinfo.value)

def test_settings_local_dev_user_enabled_allowed():
    """Ensure DEV_TEST_USER_ENABLED can be True in local/dev."""
    settings = Settings(
        ENVIRONMENT="local",
        DEV_TEST_USER_ENABLED=True,
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="password",
        POSTGRES_DB="db",
        SECRET_KEY="secret"
    )
    assert settings.DEV_TEST_USER_ENABLED is True

def test_settings_production_dev_user_disabled_allowed():
    """Ensure DEV_TEST_USER_ENABLED=False is fine in production."""
    settings = Settings(
        ENVIRONMENT="production",
        DEV_TEST_USER_ENABLED=False,
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="password",
        POSTGRES_DB="db",
        SECRET_KEY="secret"
    )
    assert settings.DEV_TEST_USER_ENABLED is False
