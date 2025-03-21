from fastapi import HTTPException
from sqlmodel import SQLModel

from app.models.query import OrderParams


def check_order_params(
    model: SQLModel, order: OrderParams, default_order: OrderParams
) -> None:
    if not order.order_by:
        order.order_by = default_order.order_by
    else:
        if order.order_by not in model.__table__.columns.keys():
            raise HTTPException(status_code=400, detail="Invalid order field")
