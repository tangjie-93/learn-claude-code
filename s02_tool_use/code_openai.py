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
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
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
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_read(path: str, limit: int | None = None) -> str:
    try:
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
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
#  OpenAI function tools: same names and inputs as s02/code.py
# ═══════════════════════════════════════════════════════════

def function_tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
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
    try:
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {"_error": "Tool arguments must be a JSON object"}
    except json.JSONDecodeError as e:
        return {"_error": f"Invalid JSON arguments: {e}"}


def as_input_item(item: Any) -> Any:
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_unset=True, mode="json")
    return item


def call_tool(name: str, args: dict[str, Any]) -> str:
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
