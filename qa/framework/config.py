"""Runtime configuration of a test run, read from the environment."""

from functools import lru_cache
from typing import Literal

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings of a test run.

    Every field is read from an environment variable with the ``QA_`` prefix, for
    example ``QA_BASE_URL``. For local runs the same variables can be put in
    ``qa/.env``; real environment variables take precedence over the file.

    Attributes:
        env: Where the tests run: ``local`` for a developer machine, ``ci`` for
            GitHub Actions.
        base_url: Origin of the system under test. The frontend and the API are
            served from it.
    """

    model_config = SettingsConfigDict(
        env_prefix="QA_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    env: Literal["local", "ci"] = "local"
    base_url: HttpUrl = HttpUrl("http://localhost:8000")

    @property
    def api_url(self) -> str:
        """Base URL of the REST API of the system under test."""
        origin = str(self.base_url).rstrip("/")
        return f"{origin}/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Return the settings of this run, read once per process."""
    return Settings()
