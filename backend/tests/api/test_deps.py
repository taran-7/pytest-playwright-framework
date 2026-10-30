import uuid
from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string

TEST_TOKEN_URL = f"{settings.API_V1_STR}/login/test-token"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def access_token(subject: uuid.UUID, expires_delta: timedelta) -> str:
    return security.create_access_token(subject, expires_delta=expires_delta)


def test_valid_token_returns_the_user(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(TEST_TOKEN_URL, headers=superuser_token_headers)

    assert r.status_code == 200
    assert r.json()["email"] == settings.FIRST_SUPERUSER


def test_missing_token_is_not_authenticated(client: TestClient) -> None:
    r = client.post(TEST_TOKEN_URL)

    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-jwt", id="malformed"),
        pytest.param(
            jwt.encode({"sub": str(uuid.uuid4())}, "another-secret", algorithm="HS256"),
            id="wrong-signature",
        ),
        pytest.param(access_token(uuid.uuid4(), timedelta(minutes=-1)), id="expired"),
    ],
)
def test_invalid_token_is_rejected(client: TestClient, token: str) -> None:
    r = client.post(TEST_TOKEN_URL, headers=bearer(token))

    assert r.status_code == 403
    assert r.json()["detail"] == "Could not validate credentials"


def test_token_of_a_missing_user_is_rejected(client: TestClient) -> None:
    token = access_token(uuid.uuid4(), timedelta(minutes=5))

    r = client.post(TEST_TOKEN_URL, headers=bearer(token))

    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_token_of_an_inactive_user_is_rejected(client: TestClient, db: Session) -> None:
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string(), is_active=False
        ),
    )
    token = access_token(user.id, timedelta(minutes=5))

    r = client.post(TEST_TOKEN_URL, headers=bearer(token))

    assert r.status_code == 400
    assert r.json()["detail"] == "Inactive user"
