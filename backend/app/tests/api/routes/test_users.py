from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import verify_password
from app.crud import user as crud
from app.models.user import User, UserCreate
from app.tests.utils.user import authentication_token_from_username
from app.tests.utils.utils import random_lower_string


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["username"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(db: Session, client: TestClient) -> None:
    headers = authentication_token_from_username(
        client=client,
        username=settings.TEST_USER,
        permissions=[f"{settings.API_V1_STR}/users/me:read"],
        db=db,
    )
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["username"] == settings.TEST_USER


def test_create_user_new_username(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    data = {"username": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    user = crud.get_user_by_username(session=db, username=username)
    assert user
    assert user.username == username


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.get_user_by_username(session=db, username=username)
    assert existing_user
    assert existing_user.username == api_user["username"]


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/0",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    assert r.json() == {"detail": "Not enough permissions"}


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    crud.create_user(session=db, user_create=user_in)
    data = {"username": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 409
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    data = {"username": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 401
    assert r.json() == {"detail": "Not enough permissions"}


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    crud.create_user(session=db, user_create=user_in)

    username2 = random_lower_string()
    password2 = random_lower_string()
    user_in2 = UserCreate(username=username2, password=password2)
    crud.create_user(session=db, user_create=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "total" in all_users
    for item in all_users["data"]:
        assert "username" in item


def test_update_user_me(client: TestClient, db: Session) -> None:
    full_name = "Updated Name"
    username = random_lower_string()
    data = {"full_name": full_name, "username": username}
    headers = authentication_token_from_username(
        client=client,
        username=username,
        permissions=[f"{settings.API_V1_STR}/users/me:update"],
        db=db,
    )
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "User updated successfully"

    user_query = select(User).where(User.username == username)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.username == username
    assert user_db.full_name == full_name


def test_register_user(client: TestClient, db: Session) -> None:
    settings.OPEN_REGISTRATION = True

    username = random_lower_string()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"username": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )

    settings.OPEN_REGISTRATION = False

    assert r.status_code == 201
    msg = r.json()
    assert msg["message"] == "User registered successfully"

    user_query = select(User).where(User.username == username)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.username == username
    assert user_db.full_name == full_name
    assert verify_password(password, user_db.hashed_password)


def test_register_user_closed(client: TestClient) -> None:
    username = random_lower_string()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"username": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Registration is closed"


def test_register_user_already_exists_error(client: TestClient) -> None:
    settings.OPEN_REGISTRATION = True

    password = random_lower_string()
    full_name = random_lower_string()
    data = {
        "username": settings.FIRST_SUPERUSER,
        "password": password,
        "full_name": full_name,
    }
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=data,
    )

    settings.OPEN_REGISTRATION = False

    assert r.status_code == 400
    assert (
        r.json()["detail"] == "The user with this username already exists in the system"
    )


def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    data = {"full_name": "Updated_full_name"}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "User updated successfully"

    user_query = select(User).where(User.username == username)
    user_db = db.exec(user_query).first()
    db.refresh(user_db)
    assert user_db
    assert user_db.full_name == "Updated_full_name"


def test_update_user_not_exists(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"full_name": "Updated_full_name"}
    r = client.put(
        f"{settings.API_V1_STR}/users/0",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


def test_update_user_username_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    username2 = random_lower_string()
    password2 = random_lower_string()
    user_in2 = UserCreate(username=username2, password=password2)
    user2 = crud.create_user(session=db, user_create=user_in2)

    data = {"username": user2.username}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this username already exists"


def test_delete_user_me(client: TestClient, db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    headers = authentication_token_from_username(
        client=client,
        username=username,
        permissions=[f"{settings.API_V1_STR}/users/me:delete"],
        db=db,
    )
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None

    user_query = select(User).where(User.id == user_id)
    user_db = db.exec(user_query).first()
    assert user_db is None


def test_delete_user_me_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/users/0",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    super_user = crud.get_user_by_username(
        session=db, username=settings.FIRST_SUPERUSER
    )
    assert super_user
    user_id = super_user.id

    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    r = client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Not enough permissions"


def test_get_user_home(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/home",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200


def test_get_user_operation_logs(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/operation-logs",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
