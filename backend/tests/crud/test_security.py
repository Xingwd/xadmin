from sqlmodel import Session

from app.crud import security as security_crud
from app.crud import user as user_crud
from app.models.user import UserCreate
from tests.utils.utils import random_lower_string


def test_authenticate_user_success(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = user_crud.create_user(session=db, user_create=user_in)

    authenticated_user = security_crud.authenticate(
        session=db, username=username, password=password
    )
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.username == username


def test_authenticate_user_wrong_password(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user_crud.create_user(session=db, user_create=user_in)

    authenticated_user = security_crud.authenticate(
        session=db, username=username, password="wrongpassword"
    )
    assert authenticated_user is None


def test_authenticate_user_nonexistent(db: Session) -> None:
    authenticated_user = security_crud.authenticate(
        session=db, username="nonexistent_user", password="somepassword"
    )
    assert authenticated_user is None


def test_authenticate_user_empty_username(db: Session) -> None:
    authenticated_user = security_crud.authenticate(
        session=db, username="", password="somepassword"
    )
    assert authenticated_user is None


def test_authenticate_user_empty_password(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user_crud.create_user(session=db, user_create=user_in)

    authenticated_user = security_crud.authenticate(
        session=db, username=username, password=""
    )
    assert authenticated_user is None


def test_authenticate_inactive_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password, is_active=False)
    user_crud.create_user(session=db, user_create=user_in)

    # authenticate only checks password, not active status
    authenticated_user = security_crud.authenticate(
        session=db, username=username, password=password
    )
    assert authenticated_user is not None
    assert authenticated_user.is_active is False
