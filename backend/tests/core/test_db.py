from collections.abc import Generator
from unittest.mock import patch

import pytest
from sqlmodel import Session, col, func, select

from app import crud
from app.core.db import init_db
from app.models import User
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture
def first_superuser_email(db: Session) -> Generator[str]:
    email = random_email()
    yield email
    for user in db.exec(select(User).where(col(User.email) == email)).all():
        db.delete(user)
    db.commit()


def test_init_db_creates_the_first_superuser(
    db: Session, first_superuser_email: str
) -> None:
    with (
        patch("app.core.db.settings.FIRST_SUPERUSER", first_superuser_email),
        patch("app.core.db.settings.FIRST_SUPERUSER_PASSWORD", random_lower_string()),
    ):
        init_db(db)

    user = crud.get_user_by_email(session=db, email=first_superuser_email)
    assert user is not None
    assert user.is_superuser


def test_init_db_does_not_duplicate_the_first_superuser(
    db: Session, first_superuser_email: str
) -> None:
    with (
        patch("app.core.db.settings.FIRST_SUPERUSER", first_superuser_email),
        patch("app.core.db.settings.FIRST_SUPERUSER_PASSWORD", random_lower_string()),
    ):
        init_db(db)
        init_db(db)

    count = db.exec(
        select(func.count())
        .select_from(User)
        .where(col(User.email) == first_superuser_email)
    ).one()
    assert count == 1
