from app.crud import operation_log as crud
from app.models.operation_log import OperationLog, OperationLogCreate


def create_random_operation_log(username: str) -> OperationLog:
    operation_log_create = OperationLogCreate(username=username)
    return crud.create_operation_log(operation_log_create=operation_log_create)
