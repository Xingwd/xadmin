from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import user as crud
from app.crud.rule import get_rule_by_name
from app.models.user import User, UserCreate, UserUpdate
from app.tests.utils.role import create_random_role
from app.tests.utils.utils import random_lower_string


def user_authentication_headers(
    *, client: TestClient, username: str, password: str
) -> dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(
    db: Session,
    password: str | None = None,
    is_active: bool = True,
) -> User:
    username = random_lower_string()
    password = password or random_lower_string()
    user_in = UserCreate(
        username=username,
        password=password,
        is_active=is_active,
    )
    user = crud.create_user(session=db, user_create=user_in)
    return user


def authentication_token_from_username(
    *,
    client: TestClient,
    username: str,
    db: Session,
    permissions: list[str] | None = None,
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    if permissions is None:
        permissions = []
    rules = [
        get_rule_by_name(session=db, name=permission) for permission in permissions
    ]
    role = create_random_role(db, rules)

    password = random_lower_string()
    user = crud.get_user_by_username(session=db, username=username)
    if not user:
        user_in_create = UserCreate(
            username=username, password=password, roles=[role.id]
        )
        user = crud.create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password, roles=[role.id])
        if not user.id:
            raise Exception("User id not set")
        user = crud.update_user(session=db, db_user=user, user_update=user_in_update)

    return user_authentication_headers(
        client=client, username=username, password=password
    )
