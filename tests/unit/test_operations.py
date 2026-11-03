"""Unit tests for arithmetic operations and helpers."""

import pytest

from app import operations
from app.database import normalize_database_url


@pytest.mark.parametrize("func, a, b, expected", [
    (operations.add, 2, 3, 5),
    (operations.subtract, 5, 3, 2),
    (operations.multiply, 4, 5, 20),
    (operations.divide, 10, 2, 5),
    (operations.add, -1.5, 1.5, 0),
])
def test_operations(func, a, b, expected):
    assert func(a, b) == expected


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        operations.divide(1, 0)


@pytest.mark.parametrize("url, expected", [
    ("postgresql://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("postgresql+psycopg://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("sqlite:///test.db", "sqlite:///test.db"),
])
def test_normalize_database_url(url, expected):
    assert normalize_database_url(url) == expected