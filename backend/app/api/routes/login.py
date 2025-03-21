from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, get_current_user
from app.core import security
from app.crud import security as crud
from app.crud.user import get_user_permissions
from app.models.security import Token
from app.models.user import User, UserPublic

router = APIRouter()


@router.post("/login/access-token")
def access_token(
    *,
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    permissions = list(get_user_permissions(user))
    token = Token(
        access_token=security.create_access_token(user.id, scopes=permissions)
    )
    user.last_login_at = datetime.now()
    session.add(user)
    session.commit()
    # 提供给中间件使用
    request.state.user = session.get(User, user.id)
    return token


@router.post("/login/test-token", response_model=UserPublic)
def test_token(
    *,
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """
    Test access token
    """
    return current_user
