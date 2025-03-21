from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.crud import security as security_crud
from app.crud import user as user_crud
from app.models.user import User, UserCreate, UserUpdate
from app.tests.utils.utils import random_lower_string


def test_create_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = user_crud.create_user(session=db, user_create=user_in)
    assert user.username == username
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = user_crud.create_user(session=db, user_create=user_in)
    authenticated_user = security_crud.authenticate(
        session=db, username=username, password=password
    )
    assert authenticated_user
    assert user.username == authenticated_user.username


def test_not_authenticate_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user = security_crud.authenticate(session=db, username=username, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = user_crud.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password, disabled=True)
    user = user_crud.create_user(session=db, user_create=user_in)
    assert user.is_active


def test_check_if_user_is_superuser(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password, is_superuser=True)
    user = user_crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = user_crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(username=username, password=password, is_superuser=True)
    user = user_crud.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserCreate(username=username, password=password, is_superuser=True)
    user = user_crud.create_user(session=db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        user_crud.update_user(session=db, db_user=user, user_update=user_in_update)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.username == user_2.username
    assert verify_password(new_password, user_2.hashed_password)
