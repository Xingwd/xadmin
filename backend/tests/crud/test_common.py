from datetime import datetime
from typing import Any, cast

import pytest
from sqlalchemy.sql.elements import ColumnElement

from app.crud.common import build_where_clause, handle_search_params
from app.models.query import CommonSearchParam, Operator
from app.models.user import User


def _compiled(clause: ColumnElement[bool]) -> str:
    return str(clause.compile(compile_kwargs={"literal_binds": True}))


def test_build_where_clause_comparison_operators() -> None:
    cases: list[tuple[Operator, str]] = [
        (Operator.eq, "= 'alice'"),
        (Operator.ne, "!= 'alice'"),
        (Operator.gt, "> 'alice'"),
        (Operator.egt, ">= 'alice'"),
        (Operator.lt, "< 'alice'"),
        (Operator.elt, "<= 'alice'"),
    ]

    for operator, expected in cases:
        clause = build_where_clause(User, "username", "alice", operator)[0]
        assert expected in _compiled(clause)


def test_build_where_clause_like_operators() -> None:
    like_clause = build_where_clause(User, "username", "ali", Operator.LIKE)[0]
    not_like_clause = build_where_clause(User, "username", "ali", Operator.NOT_LIKE)[0]

    assert "LIKE '%ali%'" in _compiled(like_clause)
    assert "NOT LIKE '%ali%'" in _compiled(not_like_clause)


def test_build_where_clause_in_operators() -> None:
    in_clause = build_where_clause(User, "username", "alice,bob", Operator.IN)[0]
    not_in_clause = build_where_clause(User, "username", "alice,bob", Operator.NOT_IN)[
        0
    ]

    assert " IN ('alice', 'bob')" in _compiled(in_clause)
    assert " NOT IN ('alice', 'bob')" in _compiled(not_in_clause)


def test_build_where_clause_range_operator() -> None:
    clauses = build_where_clause(User, "username", "alice,bob", Operator.RANGE)

    assert len(clauses) == 2
    assert ">= 'alice'" in _compiled(clauses[0])
    assert "<= 'bob'" in _compiled(clauses[1])


def test_build_where_clause_not_range_operator() -> None:
    clause = build_where_clause(User, "username", "alice,bob", Operator.NOT_RANGE)[0]
    compiled = _compiled(clause)

    assert "< 'alice'" in compiled
    assert "> 'bob'" in compiled


def test_build_where_clause_datetime_range_operator() -> None:
    clauses = build_where_clause(
        User,
        "created_at",
        "2026-01-01 00:00:00,2026-01-31 23:59:59",
        Operator.RANGE,
        render="datetime",
    )

    assert len(clauses) == 2
    assert clauses[0].right.value == datetime(2026, 1, 1, 0, 0, 0)
    assert clauses[1].right.value == datetime(2026, 1, 31, 23, 59, 59)


def test_build_where_clause_null_operators() -> None:
    null_clause = build_where_clause(User, "full_name", "", Operator.NULL)[0]
    not_null_clause = build_where_clause(User, "full_name", "", Operator.NOT_NULL)[0]

    assert "IS NULL" in _compiled(null_clause)
    assert "IS NOT NULL" in _compiled(not_null_clause)


def test_build_where_clause_unsupported_operator() -> None:
    with pytest.raises(ValueError, match="Unsupported operator"):
        build_where_clause(User, "username", "alice", cast(Any, "bad_operator"))


def test_handle_search_params_builds_quick_and_common_search_clauses() -> None:
    common_search = [
        CommonSearchParam(field="is_active", value=True, operator=Operator.eq),
        CommonSearchParam(field="full_name", value="Admin", operator=Operator.LIKE),
    ]

    clauses = handle_search_params(
        User, "alice", ["username", "full_name"], common_search
    )
    compiled = " ".join(_compiled(clause) for clause in clauses)

    assert len(clauses) == 4
    assert "username LIKE '%alice%'" in compiled
    assert "full_name LIKE '%alice%'" in compiled
    assert "is_active = true" in compiled
    assert "full_name LIKE '%Admin%'" in compiled
