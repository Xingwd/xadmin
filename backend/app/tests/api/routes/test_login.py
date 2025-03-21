from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400


def test_get_access_token_inactive_user(client: TestClient, db: Session) -> None:
    password = random_lower_string()
    user = create_random_user(db, password=password, is_active=False)
    login_data = {
        "username": user.username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400
    msg = r.json()
    assert msg["detail"] == "Inactive user"


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "username" in result


def test_invalid_access_token(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers={"Authorization": f"Bearer {random_lower_string()}"},
    )
    msg = r.json()
    assert r.status_code == 403
    assert msg["detail"] == "Could not validate credentials"


def test_access_token_with_invalid_user(client: TestClient) -> None:
    token = create_access_token(subject=0)
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    msg = r.json()
    assert r.status_code == 404
    assert msg["detail"] == "User not found"


def test_access_token_with_inactive_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db, is_active=False)
    token = create_access_token(subject=user.id)
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    msg = r.json()
    assert r.status_code == 400
    assert msg["detail"] == "Inactive user"
