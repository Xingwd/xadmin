from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models.link import RoleRuleLink, UserRoleLink
from app.models.operation_log import OperationLog
from app.models.role import Role
from app.models.rule import Rule
from app.models.user import User
from app.tests.utils.user import authentication_token_from_username
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(RoleRuleLink)
        session.execute(statement)
        statement = delete(UserRoleLink)
        session.execute(statement)
        statement = delete(Rule)
        session.execute(statement)
        statement = delete(Role)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        statement = delete(OperationLog)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_username(
        client=client, username=settings.TEST_USER, db=db
    )
