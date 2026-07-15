"""Utility functions for the demo package."""


def add(a: int, b: int) -> int:
    """Return the sum of two integers.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The sum of ``a`` and ``b``.
    """
    return a + b


def greet(name: str) -> str:
    """Return a friendly greeting for a name.

    Args:
        name: The name to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"
