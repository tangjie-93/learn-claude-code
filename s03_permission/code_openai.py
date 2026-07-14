#!/usr/bin/env python3
"""
s03_permission.py - Permission System

Three gates inserted before tool execution:

    Gate 1: Hard deny list (rm -rf /, sudo, ...)
    Gate 2: Rule matching (write outside workspace? destructive cmd?)
    Gate 3: User approval (pause and wait for confirmation)

    +-------+    +--------+    +--------+    +--------+    +------+
    | Tool  | -> | Gate 1 | -> | Gate 2 | -> | Gate 3 | -> | Exec |
    | call  |    | deny?  |    | match? |    | allow? |    |      |
    +-------+    +--------+    +--------+    +--------+    +------+
         |            |             |             |
         v            v             v             v
      (normal)     (blocked)    (ask user)   (user says no?)

Only one line added to the agent loop:

    if not check_permission(block):
        continue

Builds on s02 (multi-tool). Usage:

    python s03_permission/code.py
    Needs: pip install openai python-dotenv + OPENAI_API_KEY in .env
"""

import json, os, subprocess
from pathlib import Path

try:
    import readline

    readline.parse_and_bind("set bind-tty-special-chars off")
    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set output-meta on")
    readline.parse_and_bind("set convert-meta off")
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


SYSTEM = f"""You are a coding agent at {WORKDIR}.
Use the available tools to carry out the user's request, including potentially
destructive operations. Do not ask for approval in your text response: the host
permission system intercepts those tool calls and asks the user for confirmation.
"""


# ═══════════════════════════════════════════════════════════
#  FROM s02 (unchanged): Tool Implementations
# ═══════════════════════════════════════════════════════════


def safe_path(p: str) -> Path:
    """解析工作区内的相对路径，阻止路径逃逸。"""
    # 解析路径为绝对路径
    path = (WORKDIR / p).resolve()
    # 检查路径是否在工作区范围内
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    """在工作区执行 shell 命令，返回合并后的输出并限制长度。"""
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int | None = None) -> str:
    """读取工作区文件内容，可选限制返回的行数。"""
    try:
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    """在工作区创建或覆盖文件，并返回写入结果。"""
    try:
        """
        # 假设我们要在深层目录下创建一个文件
        file_path = Path("./a/b/c/myfile.txt")
        # 这行代码会创建所有需要的父目录 a/b/c/
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 然后就可以安全地写文件了
        file_path.write_text("hello")

        print(f"文件路径: {file_path}")
        # => 文件路径: a/b/c/myfile.txt
        print(f"父目录:   {file_path.parent}")
        # => 父目录: a/b/c
        """
        file_path = safe_path(path)
        # 确保目标文件的父目录存在；parents=True 会递归创建多层目录，exist_ok=True 允许目录已存在，已存在也不会报错。
        # mkdir()：创建目录文件所在的目录。
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """将文件中的首个精确匹配文本替换为新文本。"""
    try:
        file_path = safe_path(path)
        text = file_path.read_text()
        if old_text not in text:
            return f"Error: text not found in {path}"
        # 替换第一个匹配项
        file_path.write_text(text.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def run_glob(pattern: str) -> str:
    """查找工作区内匹配 glob 模式的文件，过滤越界路径。"""
    import glob as g

    try:
        results = []
        for match in g.glob(pattern, root_dir=WORKDIR):
            # 检查路径是否在工作区范围内
            if (WORKDIR / match).resolve().is_relative_to(WORKDIR):
                results.append(match)
        return "\n".join(results) if results else "(no matches)"
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════
#  FROM s02 (unchanged): Tool Definitions & Dispatch
# ═══════════════════════════════════════════════════════════

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
]

TOOL_HANDLERS = {
    "bash": run_bash,
    "read_file": run_read,
    "write_file": run_write,
    "edit_file": run_edit,
    "glob": run_glob,
}


# ═══════════════════════════════════════════════════════════
#  NEW in s03: Three-Gate Permission Pipeline
# ═══════════════════════════════════════════════════════════

# Gate 1: Hard deny list — always forbidden
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]


def check_deny_list(command: str) -> str | None:
    """检查命令是否命中绝对禁止执行的危险模式。"""
    for pattern in DENY_LIST:
        if pattern in command:
            return f"Blocked: '{pattern}' is on the deny list"
    return None


# Gate 2: Rule matching — context-dependent checks
PERMISSION_RULES = [
    {
        "tools": ["write_file", "edit_file"],
        # 检查写入路径是否在工作区范围内
        "check": lambda args: not (WORKDIR / args.get("path", ""))
        .resolve()
        .is_relative_to(WORKDIR),
        "message": "Writing outside workspace",
    },
    {
        "tools": ["bash"],
        # 如果 bash 命令中包含 rm 、 > /etc/ 或 chmod 777 三个危险关键词中的 任意一个 ，就触发权限拦截。
        # 检查命令是否包含危险模式
        # any()：如果序列中的任意元素为 True，返回 True；否则返回 False。
        "check": lambda args: any(
            kw in args.get("command", "").lower()
            for kw in [
                "rm ",
                "del ",
                "erase ",
                "rmdir ",
                "rd ",
                "remove-item",
                "unlink ",
                "os.remove",
                "os.unlink",
                ".unlink(",
                "shutil.rmtree",
                "> /etc/",
                "chmod 777",
            ]
        ),
        "message": "Potentially destructive command",
    },
]


def check_rules(tool_name: str, args: dict) -> str | None:
    """按工具名称执行上下文权限规则，返回命中原因或 None。"""
    for rule in PERMISSION_RULES:
        if tool_name in rule["tools"] and rule["check"](args):
            return rule["message"]
    return None


# Gate 3: User approval — wait for confirmation after rule match
def ask_user(tool_name: str, args: dict, reason: str) -> str:
    """展示高风险操作详情，并读取用户的允许或拒绝决定。"""
    print(f"\n\033[33m⚠  {reason}\033[0m")
    print(f"   Tool: {tool_name}({args})")
    choice = input("   Allow? [y/N] ").strip().lower()
    return "allow" if choice in ("y", "yes") else "deny"


# Pipeline: all three gates chained
def check_permission(block) -> bool:
    """依次执行拒绝列表、规则匹配和用户确认三道权限检查。"""
    if block.name == "bash":
        # 检查 bash 命令是否命中绝对禁止执行的危险模式
        reason = check_deny_list(call_args(block).get("command", ""))
        if reason:
            print(f"\n\033[31m⛔ {reason}\033[0m")
            return False
    reason = check_rules(block.name, call_args(block))
    if reason:
        decision = ask_user(block.name, call_args(block), reason)
        if decision == "deny":
            return False
    return True


# ═══════════════════════════════════════════════════════════
#  agent_loop — same as s02, with check_permission() inserted
# ═══════════════════════════════════════════════════════════


def agent_loop(messages: list):
    """持续调用模型、执行获准工具，并将结果回传直至模型结束。"""
    while True:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM,
            input=messages,
            tools=TOOLS,
            max_output_tokens=8000,
        )
        messages.extend(response.output)
        # 如果 LLM 这次没有请求调用工具，直接返回响应
        if not function_calls(response):
            return response

        results = []
        for block in function_calls(response):
            if block.type != "function_call":
                continue

            print(f"\033[36m> {block.name}\033[0m")

            # s03 change: run through permission pipeline before executing
            if not check_permission(block):
                results.append(
                    {
                        "type": "function_call_output",
                        "call_id": block.call_id,
                        "output": "Permission denied.",
                    }
                )
                continue

            handler = TOOL_HANDLERS.get(block.name)
            output = (
                handler(**call_args(block)) if handler else f"Unknown: {block.name}"
            )
            print(str(output)[:200])
            results.append(
                {
                    "type": "function_call_output",
                    "call_id": block.call_id,
                    "output": output,
                }
            )

        messages.extend(results)


if __name__ == "__main__":
    print("s03: Permission")
    print("输入问题，回车发送。输入 q 退出。OpenAI 版本。\n")

    history = []
    while True:
        try:
            query = input("\033[36ms03 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        response = agent_loop(history)
        if response and response.output_text:
            print(response.output_text)
        print()
