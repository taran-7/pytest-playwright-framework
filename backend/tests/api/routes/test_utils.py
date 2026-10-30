from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings

TEST_EMAIL_URL = f"{settings.API_V1_STR}/utils/test-email/"


def test_health_check(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert r.status_code == 200
    assert r.json() is True


def test_send_test_email(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    with patch("app.api.routes.utils.send_email") as send_email:
        r = client.post(
            TEST_EMAIL_URL,
            headers=superuser_token_headers,
            params={"email_to": "recipient@example.com"},
        )

    assert r.status_code == 201
    assert r.json() == {"message": "Test email sent"}
    send_email.assert_called_once()
    assert send_email.call_args.kwargs["email_to"] == "recipient@example.com"
    assert "Test email" in send_email.call_args.kwargs["subject"]


def test_send_test_email_requires_superuser(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with patch("app.api.routes.utils.send_email") as send_email:
        r = client.post(
            TEST_EMAIL_URL,
            headers=normal_user_token_headers,
            params={"email_to": "recipient@example.com"},
        )

    assert r.status_code == 403
    send_email.assert_not_called()


def test_send_test_email_requires_authentication(client: TestClient) -> None:
    r = client.post(TEST_EMAIL_URL, params={"email_to": "recipient@example.com"})
    assert r.status_code == 401


def test_send_test_email_rejects_invalid_address(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    with patch("app.api.routes.utils.send_email") as send_email:
        r = client.post(
            TEST_EMAIL_URL,
            headers=superuser_token_headers,
            params={"email_to": "not-an-email"},
        )

    assert r.status_code == 422
    send_email.assert_not_called()
