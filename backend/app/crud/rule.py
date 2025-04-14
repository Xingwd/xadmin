from sqlmodel import Session, select

from app.core.db import engine
from app.crud.common import handle_search_params
from app.models.rule import (
    Rule,
    RuleCreate,
    RuleTreePublic,
    RuleTreesPublic,
    RuleType,
    RuleUpdate,
)


def create_rule(*, session: Session, rule_create: RuleCreate) -> Rule:
    db_obj = Rule.model_validate(rule_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_rule(*, session: Session, db_rule: Rule, rule_update: RuleUpdate) -> Rule:
    rule_data = rule_update.model_dump(exclude_unset=True)
    db_rule.sqlmodel_update(rule_data)
    session.add(db_rule)
    session.commit()
    session.refresh(db_rule)
    return db_rule


def delete_rule(*, session: Session, rule: Rule) -> None:
    rule.roles = []
    session.delete(rule)
    session.commit()


def get_rules(*, session: Session) -> list[Rule]:
    rules = session.exec(select(Rule)).all()
    return rules


def get_rule_trees(
    *, session: Session, only_menus: bool = False, quick_search: str = None
) -> RuleTreesPublic:
    data = []
    menu_types = [RuleType.menu_dir, RuleType.menu_item]
    if quick_search:
        where_clause = [Rule.type.in_(menu_types)] if only_menus else []
        statement = select(Rule).where(
            *where_clause, *handle_search_params(Rule, quick_search, ["title"])
        )
        rules = session.exec(statement).all()
        data = [
            RuleTreePublic(**rule.model_dump(exclude={"children"})) for rule in rules
        ]
    else:
        statement = (
            select(Rule).where(Rule.parent_id.is_(None)).order_by(Rule.weight.desc())
        )
        rules = session.exec(statement).all()

        if only_menus:

            def build_trees(
                rules: list[Rule], menus: list[RuleTreePublic], level: int = 0
            ) -> list[RuleTreePublic]:
                for index, rule in enumerate(rules):
                    if rule.type in menu_types:
                        title_prefix = ""
                        if level > 0:
                            title_prefix = "".join(
                                [
                                    " " * level * 4,
                                    "└" if index == len(rules) - 1 else "├",
                                ]
                            )
                        title = "".join([title_prefix, rule.title])
                        menus.append(
                            RuleTreePublic(
                                **rule.model_dump(exclude={"title", "children"}),
                                title=title,
                            )
                        )
                        if rule.children:
                            build_trees(rule.children, menus, level + 1)
                return menus

            data = build_trees(rules, [])
        else:
            data = rules
    return RuleTreesPublic(data=data)


def get_rules_by_type(*, session: Session, rule_types: list[RuleType]) -> list[Rule]:
    statement = select(Rule).where(Rule.type.in_(rule_types))
    return session.exec(statement).all()


def get_full_title(rule_name: str) -> str:
    with Session(engine) as session:
        statement = select(Rule).where(Rule.name == rule_name)
        rule = session.exec(statement).first()
        titles = []
        while rule:
            titles.append(rule.title)
            rule = rule.parent
        return "-".join(titles[::-1])


def get_rule_by_name(*, session: Session, name: str) -> Rule:
    statement = select(Rule).where(Rule.name == name)
    return session.exec(statement).first()
