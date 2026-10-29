"""Fixtures shared by every test suite."""

import pytest

from framework.config import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Settings of this test run."""
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Origin of the system under test.

    Replaces the fixture of pytest-base-url, so that ``QA_BASE_URL`` is the only
    place where the target is configured.
    """
    return str(settings.base_url)
