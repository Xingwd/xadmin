from datetime import date, timedelta
from typing import Any

from sqlmodel import Session, and_, func, select
from sqlmodel.sql.expression import case

from app.core.config import settings
from app.core.security import get_password_hash
from app.crud.common import handle_search_params
from app.models.operation_log import OperationLog, OperationLogsPublic
from app.models.query import (
    CommonSearchParam,
    OrderDirection,
    OrderParams,
    PaginationParams,
)
from app.models.role import Role
from app.models.rule import Rule, UserRuleTreePublic
from app.models.security import Operation
from app.models.user import (
    User,
    UserBehaviorCount,
    UserCreate,
    UserHome,
    UsersPublic,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
            "roles": (
                [session.get(Role, id) for id in user_create.roles]
                if user_create.roles
                else []
            ),
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_update: UserUpdate) -> Any:
    user_data = user_update.model_dump(
        exclude_unset=True, exclude_none=True, exclude={"roles"}
    )
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    db_user.roles = (
        [session.get(Role, id) for id in user_update.roles] if user_update.roles else []
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_username(*, session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user


def delete_user(*, session: Session, user: User) -> None:
    user.roles = []
    session.delete(user)
    session.commit()


def get_users(
    *,
    session: Session,
    pagination: PaginationParams,
    order: OrderParams,
    quick_search: str,
    common_search: list[CommonSearchParam],
) -> UsersPublic:
    where_clause = handle_search_params(
        User, quick_search, ["username", "full_name"], common_search
    )

    total_statement = select(func.count()).select_from(User).where(*where_clause)
    total = session.exec(total_statement).one()

    statement = (
        select(User)
        .where(*where_clause)
        .order_by(
            getattr(User, order.order_by).desc()
            if order.order_direction == OrderDirection.desc
            else getattr(User, order.order_by).asc()
        )
        .offset((pagination.skip - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    users = session.exec(statement).all()

    return UsersPublic(data=users, total=total)


def get_user_permissions(user: User) -> set[str]:
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return permissions


def get_user_rules(*, session: Session, user: User) -> list[UserRuleTreePublic]:
    where_clause = [Rule.status.is_(True)]
    if not user.is_superuser:
        where_clause.append(Rule.name.in_(get_user_permissions(user)))
    statement = select(Rule).where(*where_clause)
    rules = session.exec(statement).all()
    # 构建规则字典，每个规则对象排除children属性
    rule_dict = {
        rule.id: Rule(**rule.model_dump(exclude={"children"})) for rule in rules
    }

    # 构建树形结构
    root_rules = []
    for rule in rule_dict.values():
        parent = rule_dict.get(rule.parent_id)
        if parent:  # 将子节点添加到父节点的 children 列表中
            if parent.children is None:
                parent.children = []
            parent.children.append(rule)
        else:  # 设置为根节点
            root_rules.append(rule)

    def process_children(children: list[Rule]) -> list[UserRuleTreePublic]:
        sorted_children = sorted(children, key=lambda x: x.weight, reverse=True)
        rules = []
        for child in sorted_children:
            rule = UserRuleTreePublic(**child.model_dump(exclude={"children"}))
            if child.children:
                rule.children = process_children(child.children)
            rules.append(rule)
        return rules

    return process_children(root_rules)


def get_user_logs(
    *,
    session: Session,
    pagination: PaginationParams,
    user_id: int,
) -> OperationLogsPublic:
    where_clause = [OperationLog.user_id == user_id]

    count_statement = (
        select(func.count()).select_from(OperationLog).where(*where_clause)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(OperationLog)
        .where(*where_clause)
        .order_by(OperationLog.created_at.desc())
        .offset((pagination.skip - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    logs = session.exec(statement).all()

    return OperationLogsPublic(data=logs, total=count)


def get_user_home(*, session: Session, user_id: int) -> UserHome:
    common_where_clause = [OperationLog.user_id == user_id]
    where_clause_1w = [
        OperationLog.created_at > date.today() - timedelta(days=7),
    ]
    where_clause_previous_1w = [
        OperationLog.created_at <= date.today() - timedelta(days=7),
        OperationLog.created_at > date.today() - timedelta(days=14),
    ]
    where_clause_1m = [
        OperationLog.created_at > date.today() - timedelta(days=30),
    ]
    where_clause_previous_1m = [
        OperationLog.created_at <= date.today() - timedelta(days=30),
        OperationLog.created_at > date.today() - timedelta(days=60),
    ]

    def get_count(where_clause: list = None) -> list[int, int, int, int]:
        where_clause = where_clause or []
        result = []
        for clause in [
            where_clause_1w,
            where_clause_previous_1w,
            where_clause_1m,
            where_clause_previous_1m,
        ]:
            statement = (
                select(func.count())
                .select_from(OperationLog)
                .where(*common_where_clause, *clause, *where_clause)
            )
            result.append(session.exec(statement).one())
        return result

    logins_where_clause = [
        OperationLog.request_path == f"{settings.API_V1_STR}/login/access-token"
    ]
    logins_1w, previous_logins_1w, logins_1m, previous_logins_1m = get_count(
        logins_where_clause
    )

    operations_1w, previous_operations_1w, operations_1m, previous_operations_1m = (
        get_count()
    )

    def get_detail(where_clause: list = None):
        where_clause = where_clause or []
        result = []
        for clause in [where_clause_1w, where_clause_1m]:
            statement = (
                select(
                    func.date(OperationLog.created_at).label("dt"),
                    func.count().label("count"),
                )
                .where(
                    *common_where_clause,
                    *clause,
                    *where_clause,
                )
                .group_by("dt")
                .order_by("dt")
            )
            result.append(session.exec(statement).all())
        return result

    logins_1w_detail, logins_1m_detail = get_detail(logins_where_clause)
    operations_1w_detail, operations_1m_detail = get_detail()

    def build_behavior_data(logins_detail, operations_detail, days=7):
        behavior = []
        logins_dict = {i[0]: i[1] for i in logins_detail}
        operations_dict = {i[0]: i[1] for i in operations_detail}
        for i in range(days):
            dt = date.today() - timedelta(days=days - i - 1)
            behavior.extend(
                [
                    UserBehaviorCount(
                        dt=dt,
                        behavior="登录",
                        count=logins_dict.get(dt, 0),
                    ),
                    UserBehaviorCount(
                        dt=dt,
                        behavior="操作",
                        count=operations_dict.get(dt, 0),
                    ),
                ]
            )
        return behavior

    behavior_1w = build_behavior_data(logins_1w_detail, operations_1w_detail)
    behavior_1m = build_behavior_data(logins_1m_detail, operations_1m_detail, days=30)

    ops = [op.value for op in Operation]
    exclude_where_clause = []
    for method, path in settings.USER_HOME_FEATURES_EXCLUDE_PATHS:
        exclude_where_clause.append(
            ~and_(
                OperationLog.request_method == method,
                OperationLog.request_path == path,
            )
        )
    menus_statement = (
        select(
            case(
                (
                    func.split_part(OperationLog.name, ":", -1).in_(ops),
                    func.substr(
                        OperationLog.name, 1, func.length(OperationLog.name) - 2
                    ),
                ),
                else_=OperationLog.name,
            ).label("menu"),
            func.count().label("count"),
        )
        .where(
            *common_where_clause,
            *where_clause_1m,
            *exclude_where_clause,
        )
        .group_by("menu")
        .order_by(func.count().desc())
    )
    menus = session.exec(menus_statement).all()

    home = UserHome(
        logins_1w=logins_1w,
        previous_logins_1w=previous_logins_1w,
        logins_1m=logins_1m,
        previous_logins_1m=previous_logins_1m,
        operations_1w=operations_1w,
        previous_operations_1w=previous_operations_1w,
        operations_1m=operations_1m,
        previous_operations_1m=previous_operations_1m,
        behavior_1w=behavior_1w,
        behavior_1m=behavior_1m,
        menus=menus,
    )

    return home
