from fastapi import APIRouter, HTTPException, Query, Security

from app.api.deps import SessionDep, get_current_user
from app.core.security import ApiPermissions
from app.crud import role as crud
from app.models import Message
from app.models.role import Role, RoleCreate, RolePublic, RolesPublic, RoleUpdate

router = APIRouter()


@router.get(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_ROLES.value.read.name])
    ],
    response_model=RolesPublic,
)
def read_roles(
    session: SessionDep,
    quick_search: str = Query(None, description="Quick search"),
) -> RolesPublic:
    """
    Read roles.
    """
    roles = crud.get_roles(session=session, quick_search=quick_search)
    return roles


@router.get(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_ROLES.value.read.name])
    ],
    response_model=RolePublic,
)
def read_role(session: SessionDep, id: int) -> RolePublic:
    """
    Read a role by id.
    """
    role = session.get(Role, id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_ROLES.value.create.name])
    ],
    response_model=Message,
    status_code=201,
)
def create_role(*, session: SessionDep, role_in: RoleCreate) -> Message:
    """
    Create new role.
    """
    role = crud.get_role_by_name(session=session, name=role_in.name)
    if role:
        raise HTTPException(status_code=409, detail="Role name already exists")
    crud.create_role(session=session, role_create=role_in)
    return Message(message="Role created successfully")


@router.put(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_ROLES.value.update.name])
    ],
    response_model=Message,
)
def update_role(
    *,
    session: SessionDep,
    id: int,
    role_in: RoleUpdate,
) -> Message:
    """
    Update a role.
    """
    role = session.get(Role, id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role_in.name:
        existing_role = crud.get_role_by_name(session=session, name=role_in.name)
        if existing_role and existing_role.id != id:
            raise HTTPException(
                status_code=409, detail="Role with this name already exists"
            )

    crud.update_role(session=session, db_role=role, role_update=role_in)
    return Message(message="Role updated successfully")


@router.delete(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_ROLES.value.delete.name])
    ],
    response_model=Message,
)
def delete_role(session: SessionDep, id: int) -> Message:
    """
    Delete a role.
    """
    role = session.get(Role, id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    crud.delete_role(session=session, role=role)
    return Message(message="Role deleted successfully")
