from sqlmodel import Session

from app.core.db import engine
from app.crud import operation_log as crud
from app.models.operation_log import OperationLog, OperationLogCreate
from app.models.query import (
    CommonSearchParam,
    Operator,
    OrderDirection,
    PaginationParams,
)
from app.tests.utils.utils import random_lower_string


def _create_operation_log(
    prefix: str, title_suffix: str, status_code: int
) -> OperationLog:
    return crud.create_operation_log(
        OperationLogCreate(
            username=f"{prefix}_user",
            title=f"{prefix}_{title_suffix}",
            name=f"{prefix}_{title_suffix}_name",
            request_path=f"/{prefix}/{title_suffix}",
            response_status_code=status_code,
        )
    )


def test_create_operation_log(db: Session) -> None:
    prefix = random_lower_string()[:12]

    operation_log = _create_operation_log(prefix, "created", 201)
    db_operation_log = db.get(OperationLog, operation_log.id)

    assert db_operation_log is not None
    assert db_operation_log.username == f"{prefix}_user"
    assert db_operation_log.title == f"{prefix}_created"
    assert db_operation_log.response_status_code == 201


def test_get_operation_logs_with_quick_search_order_and_pagination() -> None:
    prefix = random_lower_string()[:12]
    _create_operation_log(prefix, "a", 200)
    _create_operation_log(prefix, "b", 201)
    _create_operation_log(prefix, "c", 202)

    with Session(engine) as session:
        result = crud.get_operation_logs(
            session=session,
            pagination=PaginationParams(skip=1, limit=2),
            order_by="title",
            order_direction=OrderDirection.asc,
            quick_search=prefix,
            common_search=[],
        )

    assert result.total == 3
    assert [log.title for log in result.data] == [f"{prefix}_a", f"{prefix}_b"]


def test_get_operation_logs_with_common_search() -> None:
    prefix = random_lower_string()[:12]
    _create_operation_log(prefix, "success", 200)
    _create_operation_log(prefix, "error", 500)

    with Session(engine) as session:
        result = crud.get_operation_logs(
            session=session,
            pagination=PaginationParams(skip=1, limit=10),
            order_by="title",
            order_direction=OrderDirection.asc,
            quick_search=prefix,
            common_search=[
                CommonSearchParam(
                    field="response_status_code", value=500, operator=Operator.eq
                )
            ],
        )

    assert result.total == 1
    assert result.data[0].title == f"{prefix}_error"


def test_delete_operation_log(db: Session) -> None:
    operation_log = _create_operation_log(random_lower_string()[:12], "deleted", 204)
    db_operation_log = db.get(OperationLog, operation_log.id)
    assert db_operation_log is not None

    crud.delete_operation_log(session=db, operation_log=db_operation_log)

    assert db.get(OperationLog, operation_log.id) is None
