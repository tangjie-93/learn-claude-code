"""依赖 WORKDIR 和 CURRENT_TODOS 的工具实现。

启动时调用 configure() 一次设置工作目录。
"""

import subprocess
from pathlib import Path

_workdir = None
_current_todos: list[dict] = []


def configure(workdir: Path, current_todos: list[dict] | None = None):
    """设置工作目录和可选的 todo 列表引用。"""
    global _workdir, _current_todos
    _workdir = workdir
    if current_todos is not None:
        _current_todos = current_todos


# ── 路径安全 ──────────────────────────────────────────


def safe_path(p: str, workdir: Path | None = None) -> Path:
    """解析用户路径到工作区下，越界则抛出异常。"""
    base = workdir if workdir is not None else _workdir
    path = (base / p).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


# ── 工具实现 ──────────────────────────────────────────


def run_bash(command: str, cwd: Path | None = None) -> str:
    """通过 subprocess 执行 shell 命令，返回 stdout/stderr 或超时信息。"""
    try:
        r = subprocess.run(
            command,  # 要执行的 shell 命令，如 "ls -la"
            shell=True,  # 通过 shell 执行，支持管道、重定向等 shell 语法
            cwd=(
                cwd if cwd is not None else _workdir
            ),  # 命令执行的工作目录，默认用全局 workdir
            capture_output=True,  # 截获 stdout 和 stderr，存到 r.stdout/r.stderr，不直接打印到终端
            text=True,  # 输出自动解码为字符串（str），不加则是 bytes 类型
            encoding="utf-8",  # Windows 默认可能是 gbk，显式使用 UTF-8 以兼容仓库文本
            errors="replace",  # 遇到非 UTF-8 字节时替换，避免后台 reader 线程抛 UnicodeDecodeError
            timeout=120,  # 命令最多跑 120 秒，超时抛 TimeoutExpired 异常
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int | None = None, cwd: Path | None = None) -> str:
    """读取文件内容。可限制返回前 N 行。"""
    try:
        lines = safe_path(path, cwd).read_text(encoding="utf-8", errors="replace").splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str, cwd: Path | None = None) -> str:
    """将内容写入文件。自动创建不存在的父目录。"""
    try:
        file_path = safe_path(path, cwd)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """替换文件中首次出现的 old_text 为 new_text。"""
    try:
        file_path = safe_path(path)
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if old_text not in text:
            return f"Error: text not found in {path}"
        file_path.write_text(text.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def run_glob(pattern: str) -> str:
    """查找工作区下匹配 glob 模式的文件。"""
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
    """更新全局 todo 列表。校验状态，在控制台打印任务清单。"""
    from common.utils import _normalize_todos

    todos, error = _normalize_todos(todos)
    if error:
        return error
    _current_todos.clear()
    _current_todos.extend(todos)
    # 打印带状态图标的任务清单
    lines = ["\n\033[33m## Current Tasks\033[0m"]
    STATUS_ICONS = {
        "pending": " ",
        "in_progress": "\033[36m▸\033[0m",  # 青色箭头
        "completed": "\033[32m✓\033[0m",  # 绿色对勾
    }
    for t in _current_todos:
        icon = STATUS_ICONS[t["status"]]
        lines.append(f"  [{icon}] {t['content']}")
    print("\n".join(lines))
    return f"Updated {len(_current_todos)} tasks"
