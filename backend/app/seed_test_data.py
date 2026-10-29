import logging
from dataclasses import dataclass

from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.core.db import engine
from app.core.security import verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeedUser:
    email: str
    full_name: str
    item_count: int
    is_active: bool = True


# The superuser is created separately by app/initial_data.py.
SEED_USERS = (
    # Enough items to exercise pagination.
    SeedUser(email="qa.user@example.com", full_name="QA User", item_count=12),
    # A second owner, for access control checks between users.
    SeedUser(email="qa.other@example.com", full_name="QA Other User", item_count=2),
    # An account that must not be able to log in.
    SeedUser(
        email="qa.inactive@example.com",
        full_name="QA Inactive User",
        item_count=0,
        is_active=False,
    ),
)


def ensure_user(*, session: Session, seed_user: SeedUser, password: str) -> User:
    """Create the user, or restore password and flags if they drifted."""
    user = crud.get_user_by_email(session=session, email=seed_user.email)
    if user is None:
        return crud.create_user(
            session=session,
            user_create=UserCreate(
                email=seed_user.email,
                password=password,
                full_name=seed_user.full_name,
                is_active=seed_user.is_active,
            ),
        )

    password_matches, _ = verify_password(password, user.hashed_password)
    if (
        password_matches
        and user.full_name == seed_user.full_name
        and user.is_active == seed_user.is_active
    ):
        return user

    restored: User = crud.update_user(
        session=session,
        db_user=user,
        user_in=UserUpdate(
            password=password,
            full_name=seed_user.full_name,
            is_active=seed_user.is_active,
        ),
    )
    return restored


def ensure_items(*, session: Session, owner: User, count: int) -> int:
    """Create the missing seed items for the owner and return how many were added."""
    existing_titles = set(
        session.exec(select(Item.title).where(Item.owner_id == owner.id)).all()
    )
    created = 0
    for number in range(1, count + 1):
        title = f"Seed item {number:02d}"
        if title in existing_titles:
            continue
        crud.create_item(
            session=session,
            item_in=ItemCreate(
                title=title, description=f"Seeded item {number} of {owner.email}"
            ),
            owner_id=owner.id,
        )
        created += 1
    return created


def seed(session: Session, password: str) -> None:
    for seed_user in SEED_USERS:
        user = ensure_user(session=session, seed_user=seed_user, password=password)
        created = ensure_items(session=session, owner=user, count=seed_user.item_count)
        logger.info("Seeded %s (%d new items)", seed_user.email, created)


def main() -> None:
    if settings.FASTAPI_ENV != "development":
        raise SystemExit("Refusing to seed test data outside FASTAPI_ENV=development")
    password = settings.SEED_USER_PASSWORD
    if not password:
        raise SystemExit("SEED_USER_PASSWORD is not set")

    logger.info("Seeding test data")
    with Session(engine) as session:
        seed(session, password)
    logger.info("Test data seeded")


if __name__ == "__main__":
    main()
