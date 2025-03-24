from datetime import datetime

from sqlmodel import Session, select

from app.crud.common import handle_search_params
from app.models.role import Role, RoleCreate, RolesPublic, RoleUpdate
from app.models.rule import Rule
from app.models.user import User


def create_role(*, session: Session, role_create: RoleCreate) -> Role:
    db_role = Role.model_validate(
        role_create,
        update={
            "permissions": (
                [session.get(Rule, id) for id in role_create.permissions]
                if role_create.permissions
                else []
            ),
            "users": (
                [session.get(User, id) for id in role_create.users]
                if role_create.users
                else []
            ),
        },
    )
    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    return db_role


def update_role(*, session: Session, db_role: Role, role_update: RoleUpdate) -> Role:
    role_data = role_update.model_dump(
        exclude_unset=True, exclude={"permissions", "users"}
    )
    db_role.sqlmodel_update(role_data)

    # 更新权限
    new_permissions = (
        [session.get(Rule, id) for id in role_update.permissions]
        if role_update.permissions
        else []
    )
    if new_permissions != db_role.permissions:
        db_role.permissions = new_permissions
        db_role.updated_at = datetime.now()
    # 更新用户
    new_users = (
        [session.get(User, id) for id in role_update.users] if role_update.users else []
    )
    if new_users != db_role.users:
        db_role.users = new_users
        db_role.updated_at = datetime.now()

    session.add(db_role)
    session.commit()
    session.refresh(db_role)
    return db_role


def delete_role(*, session: Session, role: Role) -> None:
    role.permissions = []
    role.users = []
    session.delete(role)
    session.commit()


def get_roles(*, session: Session, quick_search: str = None) -> RolesPublic:
    where_clause = handle_search_params(Role, quick_search, ["name"])

    statement = select(Role).where(*where_clause).order_by(Role.id.desc())
    roles = session.exec(statement).all()
    return RolesPublic(data=roles)


def get_role_by_name(*, session: Session, name: str) -> Role | None:
    statement = select(Role).where(Role.name == name)
    return session.exec(statement).first()
