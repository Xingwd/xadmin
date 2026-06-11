import pytest
from fastapi import HTTPException

from app.api.common import check_order_params
from app.models.query import OrderDirection, OrderParams
from app.models.user import User


def test_check_order_params_none_order_by() -> None:
    order = OrderParams(order_by=None, order_direction=OrderDirection.asc)
    # Should not raise when order_by is None
    check_order_params(User, order)


def test_check_order_params_valid_field() -> None:
    order = OrderParams(order_by="username", order_direction=OrderDirection.asc)
    # Should not raise for valid field
    check_order_params(User, order)


def test_check_order_params_invalid_field() -> None:
    order = OrderParams(
        order_by="nonexistent_field", order_direction=OrderDirection.desc
    )
    with pytest.raises(HTTPException) as exc_info:
        check_order_params(User, order)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid order field"


def test_check_order_params_multiple_valid_fields() -> None:
    valid_fields = ["id", "username", "is_active", "is_superuser", "created_at"]
    for field in valid_fields:
        order = OrderParams(order_by=field, order_direction=OrderDirection.desc)
        check_order_params(User, order)


def test_check_order_params_empty_string_order_by() -> None:
    order = OrderParams(order_by="", order_direction=OrderDirection.asc)
    with pytest.raises(HTTPException) as exc_info:
        check_order_params(User, order)
    assert exc_info.value.status_code == 400
