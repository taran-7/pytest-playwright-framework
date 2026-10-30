from collections.abc import Generator

import pytest
from sqlmodel import Session, col, func, select

from app import crud
from app.core.config import settings
from app.models import Item, User, UserUpdate
from app.seed_test_data import SEED_USERS, main, seed

PASSWORD = "seed-password-123"
SEED_EMAILS = [seed_user.email for seed_user in SEED_USERS]


@pytest.fixture(autouse=True)
def clean_seed_users(db: Session) -> Generator[None]:
    yield
    for user in db.exec(select(User).where(col(User.email).in_(SEED_EMAILS))).all():
        db.delete(user)
    db.commit()


def count_items(db: Session, email: str) -> int:
    user = crud.get_user_by_email(session=db, email=email)
    assert user is not None
    return db.exec(
        select(func.count()).select_from(Item).where(Item.owner_id == user.id)
    ).one()


def test_seed_creates_users_and_items(db: Session) -> None:
    seed(db, PASSWORD)

    for seed_user in SEED_USERS:
        user = crud.get_user_by_email(session=db, email=seed_user.email)
        assert user is not None
        assert user.full_name == seed_user.full_name
        assert user.is_active == seed_user.is_active
        assert not user.is_superuser
        assert count_items(db, seed_user.email) == seed_user.item_count


def test_seed_users_can_authenticate_unless_inactive(db: Session) -> None:
    seed(db, PASSWORD)

    user = crud.authenticate(session=db, email="qa.user@example.com", password=PASSWORD)
    assert user is not None
    inactive = crud.get_user_by_email(session=db, email="qa.inactive@example.com")
    assert inactive is not None
    assert not inactive.is_active


def test_seed_is_idempotent(db: Session) -> None:
    seed(db, PASSWORD)
    seed(db, PASSWORD)

    for seed_user in SEED_USERS:
        assert count_items(db, seed_user.email) == seed_user.item_count


def test_seed_restores_drifted_user(db: Session) -> None:
    seed(db, PASSWORD)
    user = crud.get_user_by_email(session=db, email="qa.user@example.com")
    assert user is not None
    crud.update_user(
        session=db,
        db_user=user,
        user_in=UserUpdate(password="another-password-1", full_name="Renamed"),
    )

    seed(db, PASSWORD)

    restored = crud.authenticate(
        session=db, email="qa.user@example.com", password=PASSWORD
    )
    assert restored is not None
    assert restored.full_name == "QA User"


def test_main_seeds_the_test_data(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "FASTAPI_ENV", "development")
    monkeypatch.setattr(settings, "SEED_USER_PASSWORD", PASSWORD)

    main()

    for seed_user in SEED_USERS:
        assert count_items(db, seed_user.email) == seed_user.item_count
    user = crud.authenticate(session=db, email="qa.user@example.com", password=PASSWORD)
    assert user is not None


def test_main_refuses_outside_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "FASTAPI_ENV", None)

    with pytest.raises(SystemExit, match="FASTAPI_ENV=development"):
        main()


def test_main_requires_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "FASTAPI_ENV", "development")
    monkeypatch.setattr(settings, "SEED_USER_PASSWORD", None)

    with pytest.raises(SystemExit, match="SEED_USER_PASSWORD"):
        main()
