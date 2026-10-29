from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from framework.config import Settings, get_settings

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("QA_ENV", "QA_BASE_URL"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_target_the_local_stack() -> None:
    settings = Settings(_env_file=None)

    assert settings.env == "local"
    assert str(settings.base_url) == "http://localhost:8000/"
    assert settings.api_url == "http://localhost:8000/api/v1"


def test_environment_variables_override_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QA_ENV", "ci")
    monkeypatch.setenv("QA_BASE_URL", "https://staging.example.test:8443/")

    settings = Settings(_env_file=None)

    assert settings.env == "ci"
    assert settings.api_url == "https://staging.example.test:8443/api/v1"


def test_unknown_environment_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QA_ENV", "prod")

    with pytest.raises(ValidationError, match="env"):
        Settings(_env_file=None)


def test_malformed_base_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QA_BASE_URL", "not a url")

    with pytest.raises(ValidationError, match="base_url"):
        Settings(_env_file=None)


def test_env_file_is_read(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("QA_ENV=ci\nQA_BASE_URL=http://dotenv.example.test\n")

    settings = Settings(_env_file=env_file)

    assert settings.env == "ci"
    assert settings.api_url == "http://dotenv.example.test/api/v1"


def test_environment_variables_beat_the_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("QA_ENV=ci\n")
    monkeypatch.setenv("QA_ENV", "local")

    settings = Settings(_env_file=env_file)

    assert settings.env == "local"


def test_settings_are_immutable() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(ValidationError, match="frozen"):
        settings.env = "ci"  # type: ignore[misc]


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_base_url_fixture_follows_the_settings(
    base_url: str, settings: Settings
) -> None:
    assert base_url == str(settings.base_url)
