
import os
import pytest
from pydantic import ValidationError
from mitlist.core.config import Settings

def test_production_insecure_config_fails():
    """Ensure that DEV_TEST_USER_ENABLED cannot be True in production."""
    # We need to set env vars before instantiating Settings
    # Since Settings loads from env, we can pass _env_file=None to ignore .env and rely on os.environ
    # or just use environment variables.

    original_env = os.environ.get("ENVIRONMENT")
    original_dev = os.environ.get("DEV_TEST_USER_ENABLED")

    try:
        os.environ["ENVIRONMENT"] = "production"
        os.environ["DEV_TEST_USER_ENABLED"] = "true"
        # Set required fields
        os.environ["POSTGRES_SERVER"] = "localhost"
        os.environ["POSTGRES_USER"] = "u"
        os.environ["POSTGRES_PASSWORD"] = "p"
        os.environ["POSTGRES_DB"] = "d"
        os.environ["SECRET_KEY"] = "s"

        with pytest.raises(ValidationError) as excinfo:
            Settings()

        assert "DEV_TEST_USER_ENABLED cannot be True in production environment" in str(excinfo.value)

    finally:
        # Restore environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        else:
            del os.environ["ENVIRONMENT"]

        if original_dev:
            os.environ["DEV_TEST_USER_ENABLED"] = original_dev
        else:
            del os.environ["DEV_TEST_USER_ENABLED"]

def test_local_secure_config_passes():
    """Ensure that DEV_TEST_USER_ENABLED can be True in local/dev."""
    original_env = os.environ.get("ENVIRONMENT")
    original_dev = os.environ.get("DEV_TEST_USER_ENABLED")

    try:
        os.environ["ENVIRONMENT"] = "local"
        os.environ["DEV_TEST_USER_ENABLED"] = "true"
        # Set required fields
        os.environ["POSTGRES_SERVER"] = "localhost"
        os.environ["POSTGRES_USER"] = "u"
        os.environ["POSTGRES_PASSWORD"] = "p"
        os.environ["POSTGRES_DB"] = "d"
        os.environ["SECRET_KEY"] = "s"

        settings = Settings()
        assert settings.DEV_TEST_USER_ENABLED is True

    finally:
         # Restore environment
        if original_env:
            os.environ["ENVIRONMENT"] = original_env
        else:
            del os.environ["ENVIRONMENT"]

        if original_dev:
            os.environ["DEV_TEST_USER_ENABLED"] = original_dev
        else:
            del os.environ["DEV_TEST_USER_ENABLED"]
