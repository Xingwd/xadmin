import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Security

from app.api.common import check_order_params
from app.api.deps import (
    SessionDep,
    build_common_search_params,
    get_current_user,
)
from app.core.security import ApiPermissions
from app.crud import operation_log as crud
from app.models import Message
from app.models.operation_log import (
    OperationLog,
    OperationLogPublic,
    OperationLogsPublic,
)
from app.models.query import CommonSearchParam, OrderParams, PaginationParams

router = APIRouter()


@router.get(
    "/",
    dependencies=[
        Security(
            get_current_user, scopes=[ApiPermissions.OPERATION_LOGS.value.read.name]
        )
    ],
    response_model=OperationLogsPublic,
)
def read_operation_logs(
    session: SessionDep,
    pagination: PaginationParams = Depends(),
    order: OrderParams = Depends(),
    quick_search: str = Query(None, description="Quick search"),
    common_search: list[CommonSearchParam] = Depends(build_common_search_params),
) -> OperationLogsPublic:
    """
    Read operation logs
    """
    check_order_params(OperationLog, order, OrderParams(order_by="created_at"))

    logs = crud.get_operation_logs(
        session=session,
        pagination=pagination,
        order=order,
        quick_search=quick_search,
        common_search=common_search,
    )

    return logs


@router.get("/submit", dependencies=[Depends(get_current_user)])
async def submit_operation_log(rule_name: str) -> Message:
    """
    Proactively submit operation log. eg: Trigger the API to record operational logs upon accessing links or iframe menus in the frontend.
    """
    return Message(message=f"Operation log for {rule_name} generated successfully")


@router.get(
    "/{id}",
    dependencies=[
        Security(
            get_current_user, scopes=[ApiPermissions.OPERATION_LOGS.value.read.name]
        )
    ],
    response_model=OperationLogPublic,
)
def read_operation_log_by_id(id: uuid.UUID, session: SessionDep) -> OperationLogPublic:
    """
    Read a specific operation log by id.
    """
    operation_log = session.get(OperationLog, id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="Operation log not found")
    return operation_log


@router.delete(
    "/{id}",
    dependencies=[
        Security(
            get_current_user,
            scopes=[ApiPermissions.OPERATION_LOGS.value.delete.name],
        )
    ],
    response_model=Message,
)
def delete_operation_log(session: SessionDep, id: uuid.UUID) -> Message:
    """
    Delete a specific operation log.
    """
    operation_log = session.get(OperationLog, id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="Operation log not found")
    crud.delete_operation_log(session=session, operation_log=operation_log)
    return Message(message="Operation log deleted successfully")
