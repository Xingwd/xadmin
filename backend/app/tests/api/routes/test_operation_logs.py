import time
import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.operation_log import create_random_operation_log
from app.tests.utils.utils import random_lower_string


def test_read_operation_log(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    operation_log = create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/{operation_log.id}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["id"] == str(operation_log.id)


def test_read_operation_log_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Operation log not found"


def test_read_operation_log_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    operation_log = create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/{operation_log.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_read_operation_logs(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    create_random_operation_log(username=settings.FIRST_SUPERUSER)
    create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) >= 2


def test_read_operation_logs_with_order_params(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    create_random_operation_log(username=settings.FIRST_SUPERUSER)
    time.sleep(1)
    create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/",
        params={"order_by": "created_at", "order_direction": "asc"},
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) >= 2
    assert data["data"][0]["created_at"] <= data["data"][-1]["created_at"]


def test_read_operation_logs_with_error_order_params(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/",
        params={"order_by": random_lower_string()},
        headers=superuser_token_headers,
    )
    assert r.status_code == 400
    msg = r.json()
    assert msg["detail"] == "Invalid order field"


def test_delete_operation_log(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    operation_log = create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.delete(
        f"{settings.API_V1_STR}/operation-logs/{operation_log.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Operation log deleted successfully"


def test_delete_operation_log_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/operation-logs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Operation log not found"


def test_delete_operation_log_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    operation_log = create_random_operation_log(username=settings.FIRST_SUPERUSER)
    r = client.delete(
        f"{settings.API_V1_STR}/operation-logs/{operation_log.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_operation_log_active_record(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    rule_name = random_lower_string()
    r = client.get(
        f"{settings.API_V1_STR}/operation-logs/submit",
        params={"rule_name": rule_name},
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == f"Operation log for {rule_name} generated successfully"
