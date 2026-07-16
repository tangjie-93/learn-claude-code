"""Tool implementations that depend on WORKDIR and CURRENT_TODOS.

Call configure() once at startup to set the working directory.
"""

import subprocess
from pathlib import Path

_workdir = None
_current_todos: list[dict] = []


def configure(workdir: Path, current_todos: list[dict] | None = None):
    """Set the working directory and optional todo list reference."""
    global _workdir, _current_todos
    _workdir = workdir
    if current_todos is not None:
        _current_todos = current_todos


# ── Path safety ──────────────────────────────────────────

def safe_path(p: str, workdir: Path | None = None) -> Path:
    """Resolve a user-supplied path under WORKDIR. Raises if path escapes workspace."""
    base = workdir if workdir is not None else _workdir
    path = (base / p).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


# ── Tool implementations ─────────────────────────────────

def run_bash(command: str, cwd: Path | None = None) -> str:
    """Execute a shell command via subprocess. Returns stdout/stderr or timeout message."""
    try:
        r = subprocess.run(
            command, shell=True, cwd=cwd if cwd is not None else _workdir,
            capture_output=True, text=True, timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int | None = None, cwd: Path | None = None) -> str:
    """Read a file's contents. Optionally limit to first N lines."""
    try:
        lines = safe_path(path, cwd).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str, cwd: Path | None = None) -> str:
    """Write content to a file. Creates parent directories as needed."""
    try:
        file_path = safe_path(path, cwd)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """Replace the first occurrence of old_text with new_text in a file."""
    try:
        file_path = safe_path(path)
        text = file_path.read_text()
        if old_text not in text:
            return f"Error: text not found in {path}"
        file_path.write_text(text.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def run_glob(pattern: str) -> str:
    """Find files matching a glob pattern under WORKDIR."""
    import glob as g
    try:
        results = []
        for match in g.glob(pattern, root_dir=_workdir):
            if (_workdir / match).resolve().is_relative_to(_workdir):
                results.append(match)
        return "\n".join(results) if results else "(no matches)"
    except Exception as e:
        return f"Error: {e}"


def run_todo_write(todos: list) -> str:
    """Update the global todo list. Validates state, enforces only one in_progress."""
    from common.utils import _normalize_todos

    todos, error = _normalize_todos(todos)
    if error:
        return error
    _current_todos.clear()
    _current_todos.extend(todos)
    lines = ["\n\033[33m## Current Tasks\033[0m"]
    STATUS_ICONS = {
        "pending": " ",
        "in_progress": "\033[36m▸\033[0m",
        "completed": "\033[32m✓\033[0m",
    }
    for t in _current_todos:
        icon = STATUS_ICONS[t["status"]]
        lines.append(f"  [{icon}] {t['content']}")
    print("\n".join(lines))
    return f"Updated {len(_current_todos)} tasks"
