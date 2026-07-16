"""Pure utility functions — no module-level state dependencies."""

import ast
import json


def parse_arguments(raw) -> dict:
    """Parse a native Responses API function-call argument string."""
    try:
        parsed = json.loads(raw or "{}") if isinstance(raw, str) else raw
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def function_calls(response):
    """Return the native function_call output items from a response."""
    return [
        item
        for item in response.output
        if getattr(item, "type", None) == "function_call"
    ]


def call_args(call) -> dict:
    """Return a function call's parsed arguments."""
    return parse_arguments(call.arguments)


def as_input_item(item):
    """Convert an OpenAI SDK response item into a plain dict for the next request."""
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_unset=True, mode="json")
    return item


def extract_text(content) -> str:
    """Extract plain text from assistant message content (handles both str and list formats)."""
    if not isinstance(content, list):
        return str(content)
    return "\n".join(
        getattr(b, "text", "") for b in content if getattr(b, "type", None) == "text"
    )


def _normalize_todos(todos):
    """Validate and normalize todo input into a list of dicts with content/status fields."""
    if isinstance(todos, str):
        try:
            todos = json.loads(todos)
        except json.JSONDecodeError:
            try:
                todos = ast.literal_eval(todos)
            except (SyntaxError, ValueError):
                return None, "Error: todos must be a list or JSON array string"
    if not isinstance(todos, list):
        return None, "Error: todos must be a list"
    for i, t in enumerate(todos):
        if not isinstance(t, dict):
            return None, f"Error: todos[{i}] must be an object"
        if "content" not in t or "status" not in t:
            return None, f"Error: todos[{i}] missing 'content' or 'status'"
        if t["status"] not in ("pending", "in_progress", "completed"):
            return None, f"Error: todos[{i}] has invalid status '{t['status']}'"
    return todos, None
