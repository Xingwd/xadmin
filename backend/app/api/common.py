from fastapi import HTTPException
from sqlalchemy import inspect
from sqlmodel import SQLModel

from app.models.query import OrderParams


def check_order_params(
    model: type[SQLModel], order: OrderParams, default_order: OrderParams
) -> None:
    if not order.order_by:
        order.order_by = default_order.order_by
    else:
        mapper = inspect(model)
        if mapper is None or order.order_by not in mapper.columns.keys():
            raise HTTPException(status_code=400, detail="Invalid order field")
