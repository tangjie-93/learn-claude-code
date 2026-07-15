"""Tests for demo_pkg.utils."""

from demo_pkg.utils import add, greet


def test_add() -> None:
    """add returns the sum of two integers."""
    assert add(2, 3) == 5


def test_greet() -> None:
    """greet returns a friendly greeting."""
    assert greet("Claude") == "Hello, Claude!"
