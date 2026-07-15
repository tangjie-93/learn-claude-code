"""Simple greeting script."""


def greet(name: str) -> None:
    """Print a greeting for the given name.

    Args:
        name: The name to include in the greeting.
    """
    message = "Hello, " + name
    print(message)


def main() -> None:
    """Run the greeting example."""
    greet("Claude")


if __name__ == "__main__":
    main()
