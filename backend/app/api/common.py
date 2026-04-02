from fastapi import HTTPException
from sqlalchemy import inspect
from sqlmodel import SQLModel

from app.models.query import OrderParams


def check_order_params(model: type[SQLModel], order: OrderParams) -> None:
    if order.order_by is None:
        return
    else:
        mapper = inspect(model)
        if mapper is None or order.order_by not in mapper.columns.keys():
            raise HTTPException(status_code=400, detail="Invalid order field")
