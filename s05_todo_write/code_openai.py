#!/usr/bin/env python3
"""
s05: TodoWrite — add a planning tool on top of s04 hooks.

  +---------+      +-------+      +------------------+
  |  User   | ---> |  LLM  | ---> | TOOL_HANDLERS    |
  | prompt  |      |       |      |  bash            |
  +---------+      +---+---+      |  read_file       |
                        ^         |  write_file      |
                        | result  |  edit_file       |
                        +---------+  glob            |
                                      todo_write ← NEW
                                   +------------------+
                                        |
                         in-memory current_todos
                                        |
                        if rounds_since_todo >= 3:
                          inject <reminder>

Changes from s04:
  + todo_write tool + run_todo_write() implementation
  + Nag reminder (inject reminder after 3 rounds without todo update)
  + SYSTEM prompt includes "plan before execute" guidance
  + rounds_since_todo counter in agent_loop
  Loop unchanged: new tool auto-dispatches via TOOL_HANDLERS.

Run: python s05_todo_write/code.py
Needs: pip install openai python-dotenv + OPENAI_API_KEY in .env
"""

import ast, json, os, subprocess
from pathlib import Path

try:
    import readline

    readline.parse_and_bind("set bind-tty-special-chars off")
except ImportError:
    pass

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
client_kwargs = {}
if os.getenv("OPENAI_BASE_URL"):
    client_kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]

WORKDIR = Path.cwd()
client = OpenAI(**client_kwargs)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

# OpenAI Responses API helpers


def parse_arguments(raw) -> dict:
    """解析 Responses API 函数调用的参数，并保证返回字典。"""
    try:
        parsed = json.loads(raw or "{}") if isinstance(raw, str) else raw
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def function_calls(response):
    """从 Responses API 响应中筛选函数调用项。"""
    return [
        item
        for item in response.output
        if getattr(item, "type", None) == "function_call"
    ]


def call_args(call) -> dict:
    """返回已解析的函数调用参数。"""
    return parse_arguments(call.arguments)


def as_input_item(item):
    """把 OpenAI SDK 响应项转换成下一轮请求可接收的普通 dict。"""
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_unset=True, mode="json")
    return item


CURRENT_TODOS: list[dict] = []

# s05 change: SYSTEM prompt adds planning guidance
SYSTEM = (
    f"You are a coding agent at {WORKDIR}. "
    "Before starting any multi-step task, use todo_write to plan your steps. "
    "Update status as you go."
)


# ═══════════════════════════════════════════════════════════
#  FROM s02-s04 (unchanged): Tool Implementations
# ═══════════════════════════════════════════════════════════


def safe_path(p: str) -> Path:
    """解析工作区内路径，拒绝越过工作区边界的访问。"""
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    """在工作区中执行 Shell 命令并返回截断后的输出。"""
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int | None = None) -> str:
    """读取工作区文件内容，并可限制返回的行数。"""
    try:
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    """创建父目录后，将内容写入工作区中的指定文件。"""
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """在指定文件中将首次出现的目标文本替换为新文本。"""
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
    """查找匹配模式且位于工作区内的文件。"""
    import glob as g

    try:
        results = []
        for match in g.glob(pattern, root_dir=WORKDIR):
            if (WORKDIR / match).resolve().is_relative_to(WORKDIR):
                results.append(match)
        return "\n".join(results) if results else "(no matches)"
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════
#  NEW in s05: todo_write tool — plan only, no execution
# ═══════════════════════════════════════════════════════════


def _normalize_todos(todos):
    """解析并校验任务列表，返回规范化结果或错误信息。"""
    if isinstance(todos, str):
        try:
            todos = json.loads(todos)
        except json.JSONDecodeError:
            try:
                # 安全地将字符串解析为 Python 字面量（列表、字典、字符串、数字等），但不会执行任意代码。
                todos = ast.literal_eval(todos)
            except (SyntaxError, ValueError):
                return None, "Error: todos must be a list or JSON array string"
    if not isinstance(todos, list):
        return None, "Error: todos must be a list"
    # enumerate(todos) 把列表拆成 (索引, 值) 对，方便遍历时同时知道位置和内容：
    for i, t in enumerate(todos):
        if not isinstance(t, dict):
            return None, f"Error: todos[{i}] must be an object"
        if "content" not in t or "status" not in t:
            return None, f"Error: todos[{i}] missing 'content' or 'status'"
        if t["status"] not in ("pending", "in_progress", "completed"):
            return None, f"Error: todos[{i}] has invalid status '{t['status']}'"
    return todos, None


def run_todo_write(todos: list) -> str:
    """更新当前任务列表，并在终端输出各任务状态。"""
    # 全局变量 CURRENT_TODOS 用于存储当前任务列表，确保在不同函数调用之间保持一致。
    global CURRENT_TODOS
    todos, error = _normalize_todos(todos)
    if error:
        return error
    CURRENT_TODOS = todos
    lines = ["\n\033[33m## Current Tasks\033[0m"]
    # 状态 → 图标映射，定义在循环外面避免每次循环都重新创建
    STATUS_ICONS = {
        "pending": " ",
        "in_progress": "\033[36m▸\033[0m",  # 青色箭头
        "completed": "\033[32m✓\033[0m",  # 绿色对勾
    }
    for t in CURRENT_TODOS:
        icon = STATUS_ICONS[t["status"]]
        lines.append(f"  [{icon}] {t['content']}")
    print("\n".join(lines))
    return f"Updated {len(CURRENT_TODOS)} tasks"


TOOLS = [
    {
        "type": "function",
        "name": "bash",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read file contents.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write content to a file.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "type": "function",
        "name": "edit_file",
        "description": "Replace exact text in a file once.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "type": "function",
        "name": "glob",
        "description": "Find files matching a glob pattern.",
        "parameters": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    },
    # s05: new tool
    {
        "type": "function",
        "name": "todo_write",
        "description": "Create and manage a task list for your current coding session.",
        "parameters": {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required": ["content", "status"],
                    },
                }
            },
            "required": ["todos"],
        },
    },
]

TOOL_HANDLERS = {
    "bash": run_bash,
    "read_file": run_read,
    "write_file": run_write,
    "edit_file": run_edit,
    "glob": run_glob,
    "todo_write": run_todo_write,
}


# ═══════════════════════════════════════════════════════════
#  FROM s04 (unchanged): Hook System
# ═══════════════════════════════════════════════════════════

HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}


def register_hook(event: str, callback):
    """为指定生命周期事件注册回调函数。"""
    HOOKS[event].append(callback)


def trigger_hooks(event: str, *args):
    """依次触发事件回调，并返回第一个非空结果。"""
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:
            return result
    return None


# s04 hooks preserved
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if="]


def permission_hook(block):
    """在工具调用前拦截包含拒绝列表命令的 Bash 请求。"""
    if block.name == "bash":
        for p in DENY_LIST:
            if p in call_args(block).get("command", ""):
                print(f"\n\033[31m⛔ Blocked: '{p}'\033[0m")
                return "Permission denied"
    return None


def log_hook(block):
    """在工具调用前记录工具名称。"""
    print(f"\033[90m[HOOK] {block.name}\033[0m")
    return None


def context_inject_hook(query: str):
    """在提交用户提示时输出当前工作目录。"""
    print(f"\033[90m[HOOK] UserPromptSubmit: working in {WORKDIR}\033[0m")
    return None


def summary_hook(messages: list):
    """在会话结束时统计并输出工具调用次数。"""
    tool_count = sum(
        1
        for m in messages
        for b in (m.get("content") if isinstance(m.get("content"), list) else [])
        if isinstance(b, dict) and b.get("type") == "function_call_output"
    )
    print(f"\033[90m[HOOK] Stop: session used {tool_count} tool calls\033[0m")
    return None


register_hook("UserPromptSubmit", context_inject_hook)
register_hook("PreToolUse", permission_hook)
register_hook("PreToolUse", log_hook)
register_hook("Stop", summary_hook)


# ═══════════════════════════════════════════════════════════
#  agent_loop — same as s04 + nag reminder counter
# ═══════════════════════════════════════════════════════════

rounds_since_todo = 0


def agent_loop(messages: list):
    """驱动模型和工具的多轮交互，并定期提醒更新任务列表。"""
    global rounds_since_todo
    while True:
        # s05: nag reminder — inject if model hasn't updated todos for 3 rounds
        if rounds_since_todo >= 3 and messages:
            messages.append(
                {"role": "user", "content": "<reminder>Update your todos.</reminder>"}
            )
            rounds_since_todo = 0

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM,
            input=messages,
            tools=TOOLS,
            max_output_tokens=8000,
        )
        messages.extend(as_input_item(item) for item in response.output)

        if not function_calls(response):
            force = trigger_hooks("Stop", messages)
            if force:
                messages.append({"role": "user", "content": force})
                continue
            return
        # 模型调了工具 → 算一轮，+1
        rounds_since_todo += 1
        results = []
        for block in function_calls(response):
            if block.type != "function_call":
                continue

            blocked = trigger_hooks("PreToolUse", block)
            if blocked:
                results.append(
                    {
                        "type": "function_call_output",
                        "call_id": block.call_id,
                        "output": str(blocked),
                    }
                )
                continue

            handler = TOOL_HANDLERS.get(block.name)
            output = (
                handler(**call_args(block)) if handler else f"Unknown: {block.name}"
            )

            trigger_hooks("PostToolUse", block, output)

            # s05: reset nag counter when todo_write is called
            if block.name == "todo_write":
                rounds_since_todo = 0

            results.append(
                {
                    "type": "function_call_output",
                    "call_id": block.call_id,
                    "output": output,
                }
            )

        messages.extend(results)


if __name__ == "__main__":
    print("s05: TodoWrite — plan before execute, nag if you forget")
    print("Type a question, press Enter. Type q to quit. OpenAI version.\n")

    history = []
    while True:
        try:
            query = input("\033[36ms05 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        trigger_hooks("UserPromptSubmit", query)
        history.append({"role": "user", "content": query})
        response = agent_loop(history)
        if response and response.output_text:
            print(response.output_text)
        print()
