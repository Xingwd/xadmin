from fastapi import APIRouter, HTTPException, Query, Security

from app.api.deps import SessionDep, get_current_user
from app.core.security import ApiPermissions, oauth2_scopes
from app.crud import rule as crud
from app.models import Message
from app.models.rule import (
    Rule,
    RuleCreate,
    RuleTreePublic,
    RuleTreesPublic,
    RuleType,
    RuleUpdate,
)
from app.models.security import Permission

router = APIRouter()


@router.get(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.read.name])
    ],
    response_model=RuleTreesPublic,
)
def read_rules(
    session: SessionDep,
    only_menus: bool = Query(False, description="Only return menus"),
    quick_search: str = Query(None, description="Quick search"),
) -> RuleTreesPublic:
    """
    Read rules.
    """
    rules = crud.get_rules(
        session=session, only_menus=only_menus, quick_search=quick_search
    )
    return rules


@router.get(
    "/permissions",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.read.name])
    ],
    response_model=list[Permission],
)
def read_permissions(
    session: SessionDep,
    unassigned: bool = Query(False, description="Unassigned to rule"),
) -> list[Permission]:
    """
    Read permissions.
    """
    permissions, assigned_permissions = [], []

    if unassigned:
        permission_rules = crud.get_rules_by_type(
            session=session, rule_types=[RuleType.permission]
        )
        assigned_permissions = [rule.name for rule in permission_rules]

    for name, description in oauth2_scopes.items():
        if name in assigned_permissions:
            continue
        permissions.append(Permission(name=name, description=description))
    return permissions


@router.get(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.read.name])
    ],
    response_model=RuleTreePublic,
)
def read_rule(session: SessionDep, id: int) -> RuleTreePublic:
    """
    Read a rule by id.
    """
    rule = session.get(Rule, id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.post(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.create.name])
    ],
    response_model=Message,
    status_code=201,
)
def create_rule(*, session: SessionDep, rule_in: RuleCreate) -> Message:
    """
    Create new rule.
    """
    rule = crud.get_rule_by_name(session=session, name=rule_in.name)
    if rule:
        raise HTTPException(status_code=409, detail="Rule name already exists")
    crud.create_rule(session=session, rule_create=rule_in)
    return Message(message="Rule created successfully")


@router.put(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.update.name])
    ],
    response_model=Message,
)
def update_rule(
    *,
    session: SessionDep,
    id: int,
    rule_in: RuleUpdate,
) -> Message:
    """
    Update an rule.
    """
    rule = session.get(Rule, id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    if rule_in.name:
        existing_rule = crud.get_rule_by_name(session=session, name=rule_in.name)
        if existing_rule and existing_rule.id != id:
            raise HTTPException(
                status_code=409, detail="Rule with this name already exists"
            )

    crud.update_rule(session=session, db_rule=rule, rule_update=rule_in)
    return Message(message="Rule updated successfully")


@router.delete(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.RULES.value.delete.name])
    ],
    response_model=Message,
)
def delete_rule(session: SessionDep, id: int) -> Message:
    """
    Delete an rule.
    """
    rule = session.get(Rule, id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    crud.delete_rule(session=session, rule=rule)
    return Message(message="Rule deleted successfully")
