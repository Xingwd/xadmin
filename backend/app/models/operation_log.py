import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from .common import TableRecordCreatedDateTime


class OperationLogBase(SQLModel):
    user_id: int | None = Field(default=None, index=True)
    username: str | None = Field(default=None, index=True)
    name: str | None = Field(default=None)
    title: str | None = Field(default=None, index=True)
    request_method: str | None = Field(default=None)
    request_path: str | None = Field(default=None)
    request_query_params: str | None = Field(default=None)
    response_status_code: int | None = Field(default=None)


class OperationLogCreate(OperationLogBase):
    pass


class OperationLog(OperationLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: TableRecordCreatedDateTime


class OperationLogPublic(OperationLogBase):
    id: uuid.UUID
    created_at: datetime


class OperationLogsPublic(SQLModel):
    data: list[OperationLogPublic]
    total: int
