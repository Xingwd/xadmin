from sqlmodel import Session

from app.crud import rule as crud
from app.models.rule import Rule, RuleCreate, RuleType, RuleUpdate
from app.tests.utils.utils import random_lower_string


def _create_rule(
    db: Session,
    *,
    rule_type: RuleType = RuleType.menu_item,
    title: str | None = None,
    name: str | None = None,
    parent_id: int | None = None,
    weight: int = 0,
) -> int:
    rule = crud.create_rule(
        session=db,
        rule_create=RuleCreate(
            type=rule_type,
            title=title or random_lower_string(),
            name=name or random_lower_string(),
            parent_id=parent_id,
            weight=weight,
        ),
    )
    assert rule.id is not None
    return rule.id


def test_get_rule_trees_returns_nested_rules(db: Session) -> None:
    prefix = random_lower_string()[:12]
    parent_id = _create_rule(
        db,
        rule_type=RuleType.menu_dir,
        title=f"{prefix}_parent",
        name=f"{prefix}_parent",
        weight=10,
    )
    child_id = _create_rule(
        db,
        rule_type=RuleType.menu_item,
        title=f"{prefix}_child",
        name=f"{prefix}_child",
        parent_id=parent_id,
    )

    result = crud.get_rule_trees(session=db)
    parent = next(rule for rule in result.data if rule.id == parent_id)

    assert parent.children is not None
    assert any(child.id == child_id for child in parent.children)


def test_get_rule_trees_only_menus_returns_flat_menu_titles(db: Session) -> None:
    prefix = random_lower_string()[:12]
    parent_id = _create_rule(
        db,
        rule_type=RuleType.menu_dir,
        title=f"{prefix}_parent",
        name=f"{prefix}_parent",
    )
    child_id = _create_rule(
        db,
        rule_type=RuleType.menu_item,
        title=f"{prefix}_child",
        name=f"{prefix}_child",
        parent_id=parent_id,
    )
    _create_rule(
        db,
        rule_type=RuleType.permission,
        title=f"{prefix}_permission",
        name=f"{prefix}_permission",
        parent_id=parent_id,
    )

    result = crud.get_rule_trees(session=db, only_menus=True)
    rule_ids = [rule.id for rule in result.data]
    child = next(rule for rule in result.data if rule.id == child_id)

    assert parent_id in rule_ids
    assert child_id in rule_ids
    assert all(f"{prefix}_permission" != rule.name for rule in result.data)
    assert child.title.endswith(f"{prefix}_child")
    assert child.title != f"{prefix}_child"


def test_get_rule_trees_with_quick_search(db: Session) -> None:
    prefix = random_lower_string()[:12]
    matching_id = _create_rule(db, title=f"{prefix}_match", name=f"{prefix}_match")
    _create_rule(db, title=random_lower_string(), name=random_lower_string())

    result = crud.get_rule_trees(session=db, quick_search=prefix)

    assert [rule.id for rule in result.data] == [matching_id]


def test_update_rule_changes_fields(db: Session) -> None:
    rule_id = _create_rule(db)
    rule = db.get(Rule, rule_id)
    assert rule is not None
    new_title = random_lower_string()
    new_name = random_lower_string()

    updated_rule = crud.update_rule(
        session=db,
        db_rule=rule,
        rule_update=RuleUpdate(title=new_title, name=new_name),
    )

    assert updated_rule.title == new_title
    assert updated_rule.name == new_name


def test_get_rules_by_type(db: Session) -> None:
    prefix = random_lower_string()[:12]
    permission_id = _create_rule(
        db,
        rule_type=RuleType.permission,
        title=f"{prefix}_permission",
        name=f"{prefix}_permission",
    )
    _create_rule(
        db,
        rule_type=RuleType.menu_item,
        title=f"{prefix}_menu",
        name=f"{prefix}_menu",
    )

    rules = crud.get_rules_by_type(session=db, rule_types=[RuleType.permission])

    assert permission_id in [rule.id for rule in rules]
    assert all(rule.type == RuleType.permission for rule in rules)


def test_get_full_title(db: Session) -> None:
    prefix = random_lower_string()[:12]
    parent_id = _create_rule(
        db,
        rule_type=RuleType.menu_dir,
        title=f"{prefix}_parent",
        name=f"{prefix}_parent",
    )
    _create_rule(
        db,
        title=f"{prefix}_child",
        name=f"{prefix}_child",
        parent_id=parent_id,
    )

    assert crud.get_full_title(f"{prefix}_child") == f"{prefix}_parent-{prefix}_child"
    assert crud.get_full_title(None) is None


def test_delete_rule_removes_rule_and_links(db: Session) -> None:
    rule_id = _create_rule(db)
    rule = db.get(Rule, rule_id)
    assert rule is not None

    crud.delete_rule(session=db, rule=rule)

    assert db.get(Rule, rule_id) is None
