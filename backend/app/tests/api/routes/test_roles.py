from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.role import create_random_role


def test_create_role(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Foo"}
    r = client.post(
        f"{settings.API_V1_STR}/roles/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Role created successfully"


def test_create_role_name_already_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    data = {"name": role.name}
    r = client.post(
        f"{settings.API_V1_STR}/roles/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    msg = r.json()
    assert msg["detail"] == "Role name already exists"


def test_read_role(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    r = client.get(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    role_json = r.json()
    assert role_json["name"] == role.name
    assert role_json["id"] == role.id


def test_read_role_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/roles/0",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Role not found"


def test_read_role_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    r = client.get(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_read_roles(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_role(db)
    create_random_role(db)
    r = client.get(
        f"{settings.API_V1_STR}/roles/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) >= 2


def test_update_role(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    data = {"name": "Updated name"}
    r = client.put(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Role updated successfully"


def test_update_role_name_already_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    role1 = create_random_role(db)
    role2 = create_random_role(db)
    data = {"name": role1.name}
    r = client.put(
        f"{settings.API_V1_STR}/roles/{role2.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    msg = r.json()
    assert msg["detail"] == "Role with this name already exists"


def test_update_role_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated name"}
    r = client.put(
        f"{settings.API_V1_STR}/roles/0",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Role not found"


def test_update_role_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    data = {"name": "Updated name"}
    r = client.put(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_delete_role(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    r = client.delete(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Role deleted successfully"


def test_delete_role_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/roles/0",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Role not found"


def test_delete_role_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    role = create_random_role(db)
    r = client.delete(
        f"{settings.API_V1_STR}/roles/{role.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"
