from enum import Enum

from fastapi import Query
from sqlmodel import SQLModel


class PaginationParams(SQLModel):
    skip: int = Query(1, ge=1, description="The number of pages to skip")
    limit: int = Query(10, ge=1, le=1000, description="The number of items to return")


class OrderDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class OrderParams(SQLModel):
    order_by: str | None = Query(None, description="The field to order by")
    order_direction: OrderDirection = Query(
        OrderDirection.desc, description="The order direction: 'asc' or 'desc'"
    )


class Operator(str, Enum):
    eq = "eq"
    ne = "ne"
    gt = "gt"
    egt = "egt"
    lt = "lt"
    elt = "elt"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    RANGE = "RANGE"
    NOT_RANGE = "NOT RANGE"
    NULL = "NULL"
    NOT_NULL = "NOT NULL"


class CommonSearchParam(SQLModel):
    field: str
    value: str | int | bool
    operator: Operator
    render: str | None = None
