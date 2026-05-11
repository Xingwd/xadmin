from collections.abc import Sequence

from sqlmodel import Session

from app.crud import role as crud
from app.models.role import Role, RoleCreate
from app.models.rule import Rule
from app.tests.utils.utils import random_lower_string


def create_random_role(
    db: Session, rules: Sequence[Rule] | None = None, name: str | None = None
) -> Role:
    if rules is None:
        rules = []
    permissions = [rule.id for rule in rules if rule.id is not None]
    role_create = RoleCreate(
        name=name or random_lower_string(), permissions=permissions
    )
    return crud.create_role(session=db, role_create=role_create)
