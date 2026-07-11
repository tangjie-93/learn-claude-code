#!/usr/bin/env python3
"""
s02: Tool Use with OpenAI — 在 s01 OpenAI 循环基础上新增 4 个工具。

运行: python s02_tool_use/code_openai.py
需要: pip install openai python-dotenv + .env 中配置 OPENAI_API_KEY

本文件保持 s02 的工具逻辑不变:
  + bash / read_file / write_file / edit_file / glob 五个工具
  + TOOL_HANDLERS 分发映射
  + safe_path 路径安全校验

变化只在模型接口:
  + Anthropic tool_use / tool_result
  + OpenAI function_call / function_call_output
"""

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    import readline

    readline.parse_and_bind("set bind-tty-special-chars off")
    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set output-meta on")
    readline.parse_and_bind("set convert-meta off")
except ImportError:
    pass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

WORKDIR = Path.cwd()
client_kwargs = {}
if os.getenv("OPENAI_BASE_URL"):
    client_kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]

client = OpenAI(**client_kwargs)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks. Act, don't explain."


# ═══════════════════════════════════════════════════════════
#  s02 tool implementations: keep the original behavior
# ═══════════════════════════════════════════════════════════

def run_bash(command: str) -> str:
    """在工作目录执行一条 Shell 命令，并返回合并后的输出或错误信息。"""
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command,              # 要执行的命令字符串，例如 "ls -la"
            shell=True,           # 交给 shell 解析，命令才能使用管道、重定向等 shell 语法
            cwd=WORKDIR,          # 子进程的工作目录；相对路径以 WORKDIR 为基准
            capture_output=True,  # 不直接打印到终端，把标准输出和标准错误保存到 r 中
            text=True,            # 将输出解码为 str；不启用时会得到 bytes
            encoding="utf-8",     # 按 UTF-8 解码输出，避免不同系统默认编码不一致
            errors="replace",     # 遇到无法解码的字节时用替代字符表示，而不是抛出异常
            timeout=120,          # 最长允许执行 120 秒；超时会抛出 TimeoutExpired
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def safe_path(p: str) -> Path:
    """将用户路径限制在 WORKDIR 内，返回安全的规范化绝对路径。"""
    # 将用户提供的相对路径拼到工作目录，并解析 .、.. 和符号链接，得到规范的绝对路径。
    # resolve()：拼接 WORKDIR / p 后，消除 .、.. 并解析符号链接，得到真实绝对路径。
    path = (WORKDIR / p).resolve()
    # 解析后仍必须在 WORKDIR 内，防止 "../" 或符号链接访问工作区外的文件。
    # is_relative_to(WORKDIR)：确认真实路径仍在工作目录内。
    if not path.is_relative_to(WORKDIR):
        # 不安全路径立即拒绝，调用方会把错误信息返回给模型或用户。
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_read(path: str, limit: int | None = None) -> str:
    """读取工作目录内的文本文件；可选地限制返回的行数。"""
    try:
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    """在工作目录内创建或覆盖文本文件，并自动创建缺失的父目录。"""
    try:
        file_path = safe_path(path)
        # 确保目标文件的父目录存在；parents=True 会递归创建多层目录，exist_ok=True 允许目录已存在，已存在也不会报错。
        # mkdir()：创建目录文件所在的目录。
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # 将 content 写入文件；文件已存在时会覆盖其原有内容，不存在时会新建。
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    """在工作目录内的文件中，将首次出现的旧文本替换为新文本。"""
    try:
        file_path = safe_path(path)
        # 读取文件里的文件内容
        text = file_path.read_text()
        # 等同于js的 !text.includes(oldText)
        if old_text not in text:
            return f"Error: text not found in {path}"
        # 替换旧文本为新文本，只替换第一个匹配项
        # replace()：返回一个新的字符串，其中所有旧文本的出现都被替换为新文本。
        file_path.write_text(text.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


def run_glob(pattern: str) -> str:
    """按通配模式查找工作目录内的路径，并返回安全的相对路径列表。"""
    import glob as g

    try:
        results = []
        # 按 pattern（如 "*.py" 或 "src/*.py"）搜索 WORKDIR；root_dir 让返回结果保持为相对路径。
        for match in g.glob(pattern, root_dir=WORKDIR):
            # 每轮 match 是一个匹配到的路径，随后再确认它没有通过符号链接逃出工作目录。
            if (WORKDIR / match).resolve().is_relative_to(WORKDIR):
                results.append(match)
        return "\n".join(results) if results else "(no matches)"
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════
#  OpenAI function tools: same names and inputs as s02/code.py
# ═══════════════════════════════════════════════════════════

def function_tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    """根据名称、说明和参数 Schema，构造 OpenAI Responses API 的函数工具定义。"""
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        "strict": True,
    }


TOOLS = [
    function_tool(
        "bash",
        "Run a shell command.",
        {"command": {"type": "string"}},
        ["command"],
    ),
    function_tool(
        "read_file",
        "Read file contents.",
        {
            "path": {"type": "string"},
            "limit": {"type": ["integer", "null"], "description": "Maximum number of lines to read, or null."},
        },
        ["path", "limit"],
    ),
    function_tool(
        "write_file",
        "Write content to a file.",
        {"path": {"type": "string"}, "content": {"type": "string"}},
        ["path", "content"],
    ),
    function_tool(
        "edit_file",
        "Replace exact text in a file once.",
        {
            "path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
        },
        ["path", "old_text", "new_text"],
    ),
    function_tool(
        "glob",
        "Find files matching a glob pattern.",
        {"pattern": {"type": "string"}},
        ["pattern"],
    ),
]

TOOL_HANDLERS: dict[str, Callable[..., str]] = {
    "bash": run_bash,
    "read_file": run_read,
    "write_file": run_write,
    "edit_file": run_edit,
    "glob": run_glob,
}


# ═══════════════════════════════════════════════════════════
#  OpenAI Responses API glue
# ═══════════════════════════════════════════════════════════

def parse_arguments(raw: str) -> dict[str, Any]:
    """将模型返回的 JSON 参数字符串解析为字典；失败时返回可回传的错误信息。"""
    try:
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {"_error": "Tool arguments must be a JSON object"}
    except json.JSONDecodeError as e:
        return {"_error": f"Invalid JSON arguments: {e}"}


def as_input_item(item: Any) -> Any:
    """将 SDK 响应项转换为可作为下一轮 Responses API 输入的 JSON 风格数据。"""
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_unset=True, mode="json")
    return item


def call_tool(name: str, args: dict[str, Any]) -> str:
    """按工具名分发参数到处理函数，并将参数或调用错误转为文本结果。"""
    if "_error" in args:
        return args["_error"]

    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return f"Unknown: {name}"

    try:
        return handler(**args)
    except TypeError as e:
        return f"Error: invalid arguments for {name}: {e}"


def agent_loop(messages: list[dict[str, Any]]) -> Any:
    """持续请求模型、执行其函数调用并回填结果，直到模型不再调用工具。"""
    while True:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM,
            input=messages,
            tools=TOOLS,
            max_output_tokens=8000,
        )

        messages.extend(as_input_item(item) for item in response.output)

        tool_calls = [
            item for item in response.output
            if getattr(item, "type", None) == "function_call"
        ]
        if not tool_calls:
            return response

        for call in tool_calls:
            args = parse_arguments(call.arguments)
            print(f"\033[33m> {call.name}\033[0m")
            output = call_tool(call.name, args)
            print(str(output)[:200])
            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output,
            })


if __name__ == "__main__":
    print("s02: Tool Use (OpenAI) — 在 s01 基础上加了 4 个工具")
    print("输入问题，回车发送。输入 q 退出。\n")

    history: list[dict[str, Any]] = []
    while True:
        try:
            query = input("\033[36ms02-openai >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        response = agent_loop(history)
        if getattr(response, "output_text", ""):
            print(response.output_text)
        print()
