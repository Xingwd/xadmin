from sqlmodel import Session

from app.crud import role as crud
from app.models.query import OrderDirection, PaginationParams
from app.models.role import RoleCreate, RoleUpdate
from app.tests.utils.rule import create_random_rule
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_role_with_permissions_and_users(db: Session) -> None:
    rule = create_random_rule(db)
    user = create_random_user(db)
    assert rule.id is not None
    assert user.id is not None

    role = crud.create_role(
        session=db,
        role_create=RoleCreate(
            name=random_lower_string(), permissions=[rule.id], users=[user.id]
        ),
    )

    assert [permission.id for permission in role.permissions] == [rule.id]
    assert [role_user.id for role_user in role.users] == [user.id]


def test_update_role_replaces_permissions_and_users(db: Session) -> None:
    old_rule = create_random_rule(db)
    new_rule = create_random_rule(db)
    old_user = create_random_user(db)
    new_user = create_random_user(db)
    assert old_rule.id is not None
    assert new_rule.id is not None
    assert old_user.id is not None
    assert new_user.id is not None

    role = crud.create_role(
        session=db,
        role_create=RoleCreate(
            name=random_lower_string(), permissions=[old_rule.id], users=[old_user.id]
        ),
    )
    updated_name = random_lower_string()
    updated_role = crud.update_role(
        session=db,
        db_role=role,
        role_update=RoleUpdate(
            name=updated_name, permissions=[new_rule.id], users=[new_user.id]
        ),
    )

    assert updated_role.name == updated_name
    assert [permission.id for permission in updated_role.permissions] == [new_rule.id]
    assert [role_user.id for role_user in updated_role.users] == [new_user.id]


def test_delete_role_removes_role_and_links(db: Session) -> None:
    rule = create_random_rule(db)
    user = create_random_user(db)
    assert rule.id is not None
    assert user.id is not None
    role = crud.create_role(
        session=db,
        role_create=RoleCreate(
            name=random_lower_string(), permissions=[rule.id], users=[user.id]
        ),
    )
    role_id = role.id

    crud.delete_role(session=db, role=role)

    assert role_id is not None
    assert db.get(type(role), role_id) is None
    db.refresh(rule)
    db.refresh(user)
    assert all(linked_role.id != role_id for linked_role in rule.roles)
    assert all(linked_role.id != role_id for linked_role in user.roles)


def test_get_roles_with_quick_search_order_and_pagination(db: Session) -> None:
    prefix = random_lower_string()[:12]
    names = [f"{prefix}_a", f"{prefix}_b", f"{prefix}_c"]
    for name in names:
        crud.create_role(session=db, role_create=RoleCreate(name=name))

    result = crud.get_roles(
        session=db,
        pagination=PaginationParams(skip=1, limit=2),
        order_by="name",
        order_direction=OrderDirection.asc,
        quick_search=prefix,
    )

    assert result.total == 3
    assert [role.name for role in result.data] == names[:2]


def test_get_roles_desc_order_second_page(db: Session) -> None:
    prefix = random_lower_string()[:12]
    names = [f"{prefix}_a", f"{prefix}_b", f"{prefix}_c"]
    for name in names:
        crud.create_role(session=db, role_create=RoleCreate(name=name))

    result = crud.get_roles(
        session=db,
        pagination=PaginationParams(skip=2, limit=1),
        order_by="name",
        order_direction=OrderDirection.desc,
        quick_search=prefix,
    )

    assert result.total == 3
    assert [role.name for role in result.data] == [names[1]]


def test_role_update_with_empty_relationships_clears_links(db: Session) -> None:
    rule = create_random_rule(db)
    user = create_random_user(db)
    assert rule.id is not None
    assert user.id is not None
    role = crud.create_role(
        session=db,
        role_create=RoleCreate(
            name=random_lower_string(), permissions=[rule.id], users=[user.id]
        ),
    )

    updated_role = crud.update_role(
        session=db,
        db_role=role,
        role_update=RoleUpdate(name=role.name, permissions=[], users=[]),
    )

    db.refresh(updated_role)
    assert updated_role.permissions == []
    assert updated_role.users == []
