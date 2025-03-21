from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.core.security import ApiPermissions
from app.crud import user as crud_user
from app.models.rule import MenuItemType, Rule, RuleType
from app.models.user import User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.username == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud_user.create_user(session=session, user_create=user_in)

    # 初始化规则
    init_rule(session=session)


def init_rule(session: Session) -> None:
    # app.crud.rule 也依赖于 app.core.db，为了避免循环导入，在这个位置导入app.crud.rule
    from app.crud import rule as crud_rule

    home_path = "home"
    # 如果规则已存在，则跳过初始化
    if session.exec(select(Rule).where(Rule.path == home_path)).first():
        return

    # 初始化规则
    home_in = Rule(
        type=RuleType.menu_item,
        title="主页",
        name=ApiPermissions.USERS_HOME.value.resource,
        path=home_path,
        icon="el-icon-HomeFilled",
        menu_item_type=MenuItemType.tab,
        component="/src/views/home.vue",
        remark="主页banner文案",
        cache=True,
        weight=999,
        children=[
            Rule(
                type=RuleType.permission,
                title="查看",
                name=ApiPermissions.USERS_HOME.value.read.name,
            ),
        ],
    )
    crud_rule.create_rule(session=session, rule_create=home_in)

    routine_dir_in = Rule(
        type=RuleType.menu_dir,
        title="常规管理",
        name="routine",
        path="routine",
        icon="fa fa-gear",
        weight=2,
        children=[
            Rule(
                type=RuleType.menu_item,
                title="个人信息",
                name=ApiPermissions.USERS_ME.value.resource,
                path="routine/user-info",
                icon="el-icon-UserFilled",
                menu_item_type=MenuItemType.tab,
                component="/src/views/routine/userInfo.vue",
                weight=1,
                children=[
                    Rule(
                        type=RuleType.permission,
                        title="查看",
                        name=ApiPermissions.USERS_ME.value.read.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="编辑",
                        name=ApiPermissions.USERS_ME.value.update.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="删除",
                        name=ApiPermissions.USERS_ME.value.delete.name,
                    ),
                ],
            )
        ],
    )
    crud_rule.create_rule(session=session, rule_create=routine_dir_in)

    system_dir_in = Rule(
        type=RuleType.menu_dir,
        title="系统管理",
        name="system",
        path="system",
        icon="fa fa-cogs",
        weight=1,
        children=[
            Rule(
                type=RuleType.menu_item,
                title="规则管理",
                name=ApiPermissions.RULES.value.resource,
                path="system/rules",
                icon="el-icon-Grid",
                menu_item_type=MenuItemType.tab,
                component="/src/views/system/rule/index.vue",
                weight=100,
                children=[
                    Rule(
                        type=RuleType.permission,
                        title="查看",
                        name=ApiPermissions.RULES.value.read.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="添加",
                        name=ApiPermissions.RULES.value.create.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="编辑",
                        name=ApiPermissions.RULES.value.update.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="删除",
                        name=ApiPermissions.RULES.value.delete.name,
                    ),
                ],
            ),
            Rule(
                type=RuleType.menu_item,
                title="角色管理",
                name=ApiPermissions.ROLES.value.resource,
                path="system/roles",
                icon="fa fa-group",
                menu_item_type=MenuItemType.tab,
                component="/src/views/system/role/index.vue",
                weight=99,
                children=[
                    Rule(
                        type=RuleType.permission,
                        title="查看",
                        name=ApiPermissions.ROLES.value.read.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="添加",
                        name=ApiPermissions.ROLES.value.create.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="编辑",
                        name=ApiPermissions.ROLES.value.update.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="删除",
                        name=ApiPermissions.ROLES.value.delete.name,
                    ),
                ],
            ),
            Rule(
                type=RuleType.menu_item,
                title="用户管理",
                name=ApiPermissions.USERS.value.resource,
                path="system/users",
                icon="el-icon-UserFilled",
                menu_item_type=MenuItemType.tab,
                component="/src/views/system/user/index.vue",
                weight=98,
                children=[
                    Rule(
                        type=RuleType.permission,
                        title="查看",
                        name=ApiPermissions.USERS.value.read.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="添加",
                        name=ApiPermissions.USERS.value.create.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="编辑",
                        name=ApiPermissions.USERS.value.update.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="删除",
                        name=ApiPermissions.USERS.value.delete.name,
                    ),
                ],
            ),
            Rule(
                type=RuleType.menu_item,
                title="操作日志",
                name=ApiPermissions.OPERATION_LOGS.value.resource,
                path="system/operation-logs",
                icon="el-icon-List",
                menu_item_type=MenuItemType.tab,
                component="/src/views/system/operationLog/index.vue",
                weight=97,
                children=[
                    Rule(
                        type=RuleType.permission,
                        title="查看",
                        name=ApiPermissions.OPERATION_LOGS.value.read.name,
                    ),
                    Rule(
                        type=RuleType.permission,
                        title="删除",
                        name=ApiPermissions.OPERATION_LOGS.value.delete.name,
                    ),
                ],
            ),
        ],
    )
    crud_rule.create_rule(session=session, rule_create=system_dir_in)
