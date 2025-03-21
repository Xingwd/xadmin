from sqlmodel import Session

from app.crud import rule as crud
from app.models.rule import Rule, RuleCreate, RuleType
from app.tests.utils.utils import random_lower_string


def create_random_rule(db: Session) -> Rule:
    rule_create = RuleCreate(
        type=RuleType.menu_item, title=random_lower_string(), name=random_lower_string()
    )
    return crud.create_rule(session=db, rule_create=rule_create)
