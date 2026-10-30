from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.initial_data import main


def test_main_keeps_the_first_superuser(db: Session) -> None:
    main()

    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None
    assert user.is_superuser
