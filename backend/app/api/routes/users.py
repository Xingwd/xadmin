from fastapi import APIRouter, Depends, HTTPException, Query, Security

from app.api.common import check_order_params
from app.api.deps import (
    SessionDep,
    build_common_search_params,
    get_current_user,
)
from app.core.config import settings
from app.core.security import ApiPermissions
from app.crud import user as crud
from app.models import Message
from app.models.operation_log import OperationLogsPublic
from app.models.query import CommonSearchParam, OrderParams, PaginationParams
from app.models.user import (
    User,
    UserCreate,
    UserHome,
    UserMePublic,
    UserPublic,
    UserRegister,
    UserSource,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter()


@router.get(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_USERS.value.read.name])
    ],
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep,
    pagination: PaginationParams = Depends(),
    order: OrderParams = Depends(),
    quick_search: str = Query(None, description="Quick search"),
    common_search: list[CommonSearchParam] = Depends(build_common_search_params),
) -> UsersPublic:
    """
    Read users
    """
    check_order_params(User, order, OrderParams(order_by="id"))

    users = crud.get_users(
        session=session,
        pagination=pagination,
        order=order,
        quick_search=quick_search,
        common_search=common_search,
    )

    return users


@router.get("/home", response_model=UserHome)
def read_user_home(
    session: SessionDep,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS_HOME.value.read.name]
    ),
) -> UserHome:
    """
    Read current user home data.
    """
    user_home = crud.get_user_home(session=session, user_id=current_user.id)
    return user_home


@router.get("/operation-logs", response_model=OperationLogsPublic)
def read_user_operation_logs(
    session: SessionDep,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS_ME.value.read.name]
    ),
    pagination: PaginationParams = Depends(),
) -> OperationLogsPublic:
    """
    Read current user operation logs.
    """
    operation_logs = crud.get_user_logs(
        session=session,
        pagination=pagination,
        user_id=current_user.id,
    )
    return operation_logs


@router.get("/me", response_model=UserMePublic)
def read_user_me(
    session: SessionDep,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS_ME.value.read.name]
    ),
) -> UserMePublic:
    """
    Read current user.
    """
    user_me = UserMePublic(
        **current_user.model_dump(),
        rules=crud.get_user_rules(session=session, user=current_user),
    )
    return user_me


@router.patch("/me", response_model=Message)
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS_ME.value.update.name]
    ),
) -> Message:
    """
    Update own user.
    """
    db_user = session.get(User, current_user.id)
    crud.update_user_me(
        session=session,
        db_user=db_user,
        user_update_me=user_in,
    )
    return Message(message="User updated successfully")


@router.delete("/me", response_model=Message)
def delete_user_me(
    session: SessionDep,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS_ME.value.delete.name]
    ),
) -> Message:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    user = session.get(User, current_user.id)
    crud.delete_user(session=session, user=user)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=Message, status_code=201)
def register_user(session: SessionDep, user_in: UserRegister) -> Message:
    """
    Create new user without the need to be logged in.
    """
    if not settings.OPEN_REGISTRATION:
        raise HTTPException(status_code=403, detail="Registration is closed")

    user = crud.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_create = UserCreate.model_validate(
        user_in, update={"source": UserSource.signup}
    )
    user = crud.create_user(session=session, user_create=user_create)
    return Message(message="User registered successfully")


@router.get(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_USERS.value.read.name])
    ],
    response_model=UserPublic,
)
def read_user_by_id(id: int, session: SessionDep) -> UserPublic:
    """
    Read a specific user by id.
    """
    user = session.get(User, id)
    return user


@router.post(
    "/",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_USERS.value.create.name])
    ],
    response_model=Message,
    status_code=201,
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Message:
    """
    Create new user.
    """
    user = crud.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this username already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)

    return Message(message="User created successfully")


@router.put(
    "/{id}",
    dependencies=[
        Security(get_current_user, scopes=[ApiPermissions.V1_USERS.value.update.name])
    ],
    response_model=Message,
)
def update_user(
    *,
    session: SessionDep,
    id: int,
    user_in: UserUpdate,
) -> Message:
    """
    Update a user.
    """

    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.username:
        existing_user = crud.get_user_by_username(
            session=session, username=user_in.username
        )
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=409, detail="User with this username already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_update=user_in)
    return Message(message="User updated successfully")


@router.delete(
    "/{id}",
    response_model=Message,
)
def delete_user(
    session: SessionDep,
    id: int,
    current_user: User = Security(
        get_current_user, scopes=[ApiPermissions.V1_USERS.value.delete.name]
    ),
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Users are not allowed to delete themselves"
        )
    crud.delete_user(session=session, user=user)
    return Message(message="User deleted successfully")
