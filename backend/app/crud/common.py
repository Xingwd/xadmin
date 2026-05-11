from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import true
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import SQLModel, or_

from app.models.query import CommonSearchParam, Operator


def build_where_clause(
    model_class: type[SQLModel],
    field: str,
    value: str | int | bool,
    operator: Operator,
    render: str | None = None,
) -> Sequence[ColumnElement[bool]]:
    if operator == Operator.eq:
        return [getattr(model_class, field) == value]
    elif operator == Operator.ne:
        return [getattr(model_class, field) != value]
    elif operator == Operator.gt:
        return [getattr(model_class, field) > value]
    elif operator == Operator.egt:
        return [getattr(model_class, field) >= value]
    elif operator == Operator.lt:
        return [getattr(model_class, field) < value]
    elif operator == Operator.elt:
        return [getattr(model_class, field) <= value]
    elif operator == Operator.LIKE:
        return [getattr(model_class, field).like(f"%{value}%")]
    elif operator == Operator.NOT_LIKE:
        return [getattr(model_class, field).not_like(f"%{value}%")]
    elif operator == Operator.IN:
        return [getattr(model_class, field).in_(str(value).split(","))]
    elif operator == Operator.NOT_IN:
        return [getattr(model_class, field).not_in(str(value).split(","))]
    elif operator in [Operator.RANGE, Operator.NOT_RANGE]:
        start, end = str(value).split(",")
        clause, or_clause = [], []
        if start:
            if render == "datetime":
                start_datetime = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                clause.append(getattr(model_class, field) >= start_datetime)
                or_clause.append(getattr(model_class, field) < start_datetime)
            else:
                clause.append(getattr(model_class, field) >= start)
                or_clause.append(getattr(model_class, field) < start)
        if end:
            if render == "datetime":
                end_datetime = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                clause.append(getattr(model_class, field) <= end_datetime)
                or_clause.append(getattr(model_class, field) > end_datetime)
            else:
                clause.append(getattr(model_class, field) <= end)
                or_clause.append(getattr(model_class, field) > end)
        if operator == Operator.NOT_RANGE:
            clause = [or_(*or_clause)]
        return clause
    elif operator == Operator.NULL:
        return [getattr(model_class, field).is_(None)]
    elif operator == Operator.NOT_NULL:
        return [getattr(model_class, field).is_not(None)]
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def handle_search_params(
    model_class: type[SQLModel],
    quick_search: str,
    quick_search_fields: Sequence[str],
    common_search: Sequence[CommonSearchParam] | None = None,
) -> Sequence[ColumnElement[bool]]:
    where_clause: list[ColumnElement[bool]] = [true()]
    if quick_search:
        or_clause = [
            build_where_clause(model_class, field, quick_search, Operator.LIKE)[0]
            for field in quick_search_fields
        ]
        where_clause.append(or_(*or_clause))
    if common_search:
        for item in common_search:
            where_clause.extend(
                build_where_clause(
                    model_class, item.field, item.value, item.operator, item.render
                )
            )
    return where_clause
