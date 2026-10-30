from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings

VALID_VALUES: dict[str, Any] = {
    "SECRET_KEY": "a-secret-key-that-is-not-the-default",
    "PROJECT_NAME": "Test Project",
    "DATABASE_URL": "postgresql+psycopg://user:db-password@localhost/app",
    "FIRST_SUPERUSER": "admin@example.com",
    "FIRST_SUPERUSER_PASSWORD": "admin-password",
    "FASTAPI_ENV": None,
}


def make_settings(**overrides: Any) -> Settings:
    """Build settings from explicit values only, ignoring .env and the environment."""
    return Settings(_env_file=None, **{**VALID_VALUES, **overrides})


@pytest.mark.parametrize(
    "scheme",
    [
        pytest.param("postgres://", id="postgres"),
        pytest.param("postgresql://", id="postgresql"),
        pytest.param("postgresql+psycopg://", id="already-psycopg"),
    ],
)
def test_database_url_uses_the_psycopg_driver(scheme: str) -> None:
    settings = make_settings(DATABASE_URL=f"{scheme}user:db-password@localhost/app")

    assert str(settings.DATABASE_URL).startswith("postgresql+psycopg://")


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("SECRET_KEY", id="secret-key"),
        pytest.param("FIRST_SUPERUSER_PASSWORD", id="superuser-password"),
        pytest.param("DATABASE_URL", id="database-password"),
    ],
)
def test_default_secrets_are_rejected_outside_development(name: str) -> None:
    value = (
        "postgresql+psycopg://user:changethis@localhost/app"
        if name == "DATABASE_URL"
        else "changethis"
    )

    with pytest.raises(ValidationError, match="changethis"):
        make_settings(**{name: value})


def test_default_secrets_only_warn_in_development() -> None:
    with pytest.warns(UserWarning, match="changethis"):
        settings = make_settings(SECRET_KEY="changethis", FASTAPI_ENV="development")

    assert settings.SECRET_KEY == "changethis"


def test_emails_are_enabled_only_with_a_host_and_a_sender() -> None:
    assert not make_settings().emails_enabled
    assert not make_settings(SMTP_HOST="smtp.example.com").emails_enabled
    assert not make_settings(EMAILS_FROM_EMAIL="from@example.com").emails_enabled
    assert make_settings(
        SMTP_HOST="smtp.example.com", EMAILS_FROM_EMAIL="from@example.com"
    ).emails_enabled


def test_sender_name_defaults_to_the_project_name() -> None:
    assert make_settings().EMAILS_FROM_NAME == "Test Project"
    assert make_settings(EMAILS_FROM_NAME="Sender").EMAILS_FROM_NAME == "Sender"
