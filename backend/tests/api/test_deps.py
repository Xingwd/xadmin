import json

import pytest

from app.api.deps import build_common_search_params
from app.models.query import CommonSearchParam, Operator


def test_build_common_search_params_none() -> None:
    result = build_common_search_params(None)
    assert result == []


def test_build_common_search_params_empty_string() -> None:
    result = build_common_search_params("")
    assert result == []


def test_build_common_search_params_single_param() -> None:
    common_search = json.dumps(
        [{"field": "username", "value": "alice", "operator": "eq"}]
    )
    result = build_common_search_params(common_search)
    assert len(result) == 1
    assert isinstance(result[0], CommonSearchParam)
    assert result[0].field == "username"
    assert result[0].value == "alice"
    assert result[0].operator == Operator.eq


def test_build_common_search_params_multiple_params() -> None:
    common_search = json.dumps(
        [
            {"field": "username", "value": "alice", "operator": "eq"},
            {"field": "is_active", "value": True, "operator": "eq"},
        ]
    )
    result = build_common_search_params(common_search)
    assert len(result) == 2
    assert result[0].field == "username"
    assert result[1].field == "is_active"
    assert result[1].value is True


def test_build_common_search_params_with_render() -> None:
    common_search = json.dumps(
        [
            {
                "field": "created_at",
                "value": "2026-01-01 00:00:00,2026-01-31 23:59:59",
                "operator": "RANGE",
                "render": "datetime",
            }
        ]
    )
    result = build_common_search_params(common_search)
    assert len(result) == 1
    assert result[0].field == "created_at"
    assert result[0].render == "datetime"


def test_build_common_search_params_invalid_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        build_common_search_params("invalid json")


def test_build_common_search_params_various_operators() -> None:
    operators = [
        "eq",
        "ne",
        "gt",
        "egt",
        "lt",
        "elt",
        "LIKE",
        "NOT LIKE",
        "IN",
        "NOT IN",
        "RANGE",
        "NOT RANGE",
        "NULL",
        "NOT NULL",
    ]
    for op in operators:
        common_search = json.dumps(
            [{"field": "username", "value": "test", "operator": op}]
        )
        result = build_common_search_params(common_search)
        assert len(result) == 1
        assert result[0].operator == Operator(op)
