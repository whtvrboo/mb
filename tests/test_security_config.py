import pytest
from pydantic import ValidationError

from mitlist.core.config import Settings


def test_production_security_config():
    """Verify that DEV_TEST_USER_ENABLED cannot be True in production."""
    with pytest.raises(ValidationError) as excinfo:
        Settings(
            ENVIRONMENT="production",
            DEV_TEST_USER_ENABLED=True,
            # Provide dummy values for required fields
            POSTGRES_SERVER="localhost",
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="password",
            POSTGRES_DB="db",
            SECRET_KEY="secret",
        )

    # Check that the error message is correct
    assert "DEV_TEST_USER_ENABLED must be False in production environment" in str(excinfo.value)


def test_dev_security_config_allowed():
    """Verify that DEV_TEST_USER_ENABLED is allowed in development."""
    settings = Settings(
        ENVIRONMENT="local",
        DEV_TEST_USER_ENABLED=True,
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="user",
        POSTGRES_PASSWORD="password",
        POSTGRES_DB="db",
        SECRET_KEY="secret",
    )
    assert settings.DEV_TEST_USER_ENABLED is True
