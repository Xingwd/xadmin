from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import rule as crud
from app.models.rule import RuleCreate, RuleType
from app.tests.utils.rule import create_random_rule
from app.tests.utils.utils import random_lower_string


def test_create_rule(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"type": RuleType.menu_item, "title": "Title", "name": "Name"}
    r = client.post(
        f"{settings.API_V1_STR}/rules/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Rule created successfully"


def test_create_rule_type_not_exists(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"type": "not_exists", "title": "Title", "name": "Name"}
    r = client.post(
        f"{settings.API_V1_STR}/rules/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 422
    msg = r.json()
    assert (
        msg["detail"][0]["msg"]
        == "Input should be 'menu_dir', 'menu_item' or 'permission'"
    )


def test_create_rule_name_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    type = RuleType.menu_item
    title = random_lower_string()
    name = random_lower_string()
    crud.create_rule(
        session=db, rule_create=RuleCreate(type=type, title=title, name=name)
    )

    data = {"type": type, "title": title, "name": name}
    r = client.post(
        f"{settings.API_V1_STR}/rules/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    msg = r.json()
    assert msg["detail"] == "Rule name already exists"


def test_read_rule(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    r = client.get(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    rule_json = r.json()
    assert rule_json["type"] == rule.type
    assert rule_json["title"] == rule.title
    assert rule_json["name"] == rule.name


def test_read_rule_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/rules/0",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Rule not found"


def test_read_rule_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    r = client.get(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_read_rules(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_rule(db)
    create_random_rule(db)
    r = client.get(
        f"{settings.API_V1_STR}/rules/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) >= 2


def test_read_rules_only_menus(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_rule(db)
    create_random_rule(db)
    r = client.get(
        f"{settings.API_V1_STR}/rules/",
        params={"only_menus": True},
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) >= 2


def test_update_rule(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    data = {"title": "Updated title", "name": "Updated name"}
    r = client.put(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Rule updated successfully"


def test_update_rule_name_already_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    rule1 = create_random_rule(db)
    rule2 = create_random_rule(db)
    data = {"title": "Updated title", "name": rule1.name}
    r = client.put(
        f"{settings.API_V1_STR}/rules/{rule2.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    msg = r.json()
    assert msg["detail"] == "Rule with this name already exists"


def test_update_rule_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "name": "Updated name"}
    r = client.put(
        f"{settings.API_V1_STR}/rules/0",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    msg = r.json()
    assert msg["detail"] == "Rule not found"


def test_update_rule_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    data = {
        "type": RuleType.menu_item,
        "title": "Updated title",
        "name": "Updated name",
    }
    r = client.put(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_delete_rule(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    r = client.delete(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    msg = r.json()
    assert msg["message"] == "Rule deleted successfully"


def test_delete_rule_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/rules/0",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Rule not found"


def test_delete_rule_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    rule = create_random_rule(db)
    r = client.delete(
        f"{settings.API_V1_STR}/rules/{rule.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 401
    msg = r.json()
    assert msg["detail"] == "Not enough permissions"


def test_get_permissions(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/rules/permissions",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
