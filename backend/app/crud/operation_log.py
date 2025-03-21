from sqlmodel import Session, func, select

from app.core.db import engine
from app.crud.common import handle_search_params
from app.models.operation_log import (
    OperationLog,
    OperationLogCreate,
    OperationLogsPublic,
)
from app.models.query import (
    CommonSearchParam,
    OrderDirection,
    OrderParams,
    PaginationParams,
)


def create_operation_log(operation_log_create: OperationLogCreate) -> OperationLog:
    db_obj = OperationLog.model_validate(operation_log_create)
    with Session(engine) as session:
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
    return db_obj


def delete_operation_log(*, session: Session, operation_log: OperationLog) -> None:
    session.delete(operation_log)
    session.commit()


def get_operation_logs(
    *,
    session: Session,
    pagination: PaginationParams,
    order: OrderParams,
    quick_search: str,
    common_search: list[CommonSearchParam],
) -> OperationLogsPublic:
    where_clause = handle_search_params(
        OperationLog, quick_search, ["title"], common_search
    )

    total_statement = (
        select(func.count()).select_from(OperationLog).where(*where_clause)
    )
    total = session.exec(total_statement).one()

    statement = (
        select(OperationLog)
        .where(*where_clause)
        .order_by(
            getattr(OperationLog, order.order_by).desc()
            if order.order_direction == OrderDirection.desc
            else getattr(OperationLog, order.order_by).asc()
        )
        .offset((pagination.skip - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    logs = session.exec(statement).all()

    return OperationLogsPublic(data=logs, total=total)
