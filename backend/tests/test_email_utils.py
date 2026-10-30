from contextlib import ExitStack
from typing import Any
from unittest.mock import patch

import pytest

from app.core.config import settings
from app.utils import (
    generate_new_account_email,
    generate_password_reset_token,
    generate_reset_password_email,
    generate_test_email,
    send_email,
    verify_password_reset_token,
)


def sent_smtp_options(**smtp_settings: Any) -> dict[str, Any]:
    """Send an email with the given SMTP settings and return the SMTP options used."""
    defaults: dict[str, Any] = {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": 2525,
        "SMTP_TLS": False,
        "SMTP_SSL": False,
        "SMTP_USER": None,
        "SMTP_PASSWORD": None,
        "EMAILS_FROM_EMAIL": "from@example.com",
    }
    with ExitStack() as stack:
        message_class = stack.enter_context(patch("app.utils.emails.message.Message"))
        for name, value in {**defaults, **smtp_settings}.items():
            stack.enter_context(patch.object(settings, name, value))
        send_email(email_to="to@example.com", subject="Hi", html_content="<p>Hi</p>")

    send = message_class.return_value.send
    send.assert_called_once()
    assert send.call_args.kwargs["to"] == "to@example.com"
    options: dict[str, Any] = send.call_args.kwargs["smtp"]
    return options


@pytest.mark.parametrize(
    ("tls", "ssl", "expected"),
    [
        pytest.param(True, False, {"tls": True}, id="tls"),
        pytest.param(False, True, {"ssl": True}, id="ssl"),
        pytest.param(True, True, {"tls": True}, id="tls-wins-over-ssl"),
        pytest.param(False, False, {}, id="plain"),
    ],
)
def test_send_email_transport_security(
    tls: bool, ssl: bool, expected: dict[str, bool]
) -> None:
    options = sent_smtp_options(SMTP_TLS=tls, SMTP_SSL=ssl)

    assert options == {"host": "smtp.example.com", "port": 2525, **expected}


def test_send_email_logs_in_when_credentials_are_set() -> None:
    options = sent_smtp_options(SMTP_USER="mailer", SMTP_PASSWORD="mail-secret")

    assert options["user"] == "mailer"
    assert options["password"] == "mail-secret"


def test_send_email_requires_email_configuration() -> None:
    with (
        patch.object(settings, "SMTP_HOST", None),
        pytest.raises(AssertionError, match="no provided configuration"),
    ):
        send_email(email_to="to@example.com")


def test_generate_test_email() -> None:
    email = generate_test_email("to@example.com")

    assert email.subject == f"{settings.PROJECT_NAME} - Test email"
    assert "to@example.com" in email.html_content


def test_generate_reset_password_email_links_to_the_frontend() -> None:
    email = generate_reset_password_email(
        email_to="to@example.com", email="user@example.com", token="the-token"
    )

    assert "user@example.com" in email.subject
    assert f"{settings.FRONTEND_HOST}/reset-password?token=the-token" in (
        email.html_content
    )


def test_generate_new_account_email() -> None:
    email = generate_new_account_email(
        email_to="to@example.com", username="user@example.com", password="pw-123456"
    )

    assert "user@example.com" in email.subject
    assert "pw-123456" in email.html_content


def test_password_reset_token_round_trip() -> None:
    token = generate_password_reset_token(email="user@example.com")

    assert verify_password_reset_token(token) == "user@example.com"


def test_tampered_password_reset_token_is_rejected() -> None:
    token = generate_password_reset_token(email="user@example.com")

    assert verify_password_reset_token(f"{token}x") is None
    assert verify_password_reset_token("garbage") is None
