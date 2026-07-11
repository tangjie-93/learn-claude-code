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
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

from openai import OpenAI
from types import SimpleNamespace
from dotenv import load_dotenv

load_dotenv(override=True)
client_kwargs = {}
if os.getenv("OPENAI_BASE_URL"):
    client_kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]

WORKDIR = Path.cwd()
client = OpenAI(**client_kwargs)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

# ═══════════════════════════════════════════════════════════
#  OpenAI Responses API compatibility helpers
#  Keep the chapter logic below unchanged: tools still return tool_use-like
#  blocks to the loop, while this layer maps them to function_call internally.
# ═══════════════════════════════════════════════════════════

def _block_type(block):
    return block.get("type") if isinstance(block, dict) else getattr(block, "type", None)


def _block_attr(block, name, default=None):
    return block.get(name, default) if isinstance(block, dict) else getattr(block, name, default)


def _json_arguments(value) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value or {}, ensure_ascii=False)


def _to_openai_input(messages: list) -> list:
    converted = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if isinstance(content, str):
            converted.append({"role": role, "content": content})
            continue
        if not isinstance(content, list):
            converted.append({"role": role, "content": str(content)})
            continue

        text_parts = []
        for block in content:
            kind = _block_type(block)
            if kind == "text":
                text = _block_attr(block, "text", "")
                if text:
                    text_parts.append(str(text))
            elif kind == "tool_use":
                if text_parts:
                    converted.append({"role": "assistant", "content": "\n".join(text_parts)})
                    text_parts = []
                converted.append({
                    "type": "function_call",
                    "call_id": _block_attr(block, "id"),
                    "name": _block_attr(block, "name"),
                    "arguments": _json_arguments(_block_attr(block, "input", {})),
                })
            elif kind == "tool_result":
                if text_parts:
                    converted.append({"role": role, "content": "\n".join(text_parts)})
                    text_parts = []
                converted.append({
                    "type": "function_call_output",
                    "call_id": _block_attr(block, "tool_use_id"),
                    "output": str(_block_attr(block, "content", "")),
                })

        if text_parts:
            converted.append({"role": role, "content": "\n".join(text_parts)})
    return converted


def _to_openai_tools(tools: list | None) -> list | None:
    if not tools:
        return None
    converted = []
    for tool in tools:
        if tool.get("type") == "function":
            converted.append(tool)
            continue
        schema = dict(tool.get("input_schema") or tool.get("parameters") or {"type": "object"})
        schema.setdefault("type", "object")
        converted.append({
            "type": "function",
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": schema,
        })
    return converted


def _parse_arguments(raw) -> dict:
    try:
        parsed = json.loads(raw or "{}") if isinstance(raw, str) else raw
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _from_openai_response(response):
    content = []
    for item in getattr(response, "output", []) or []:
        kind = getattr(item, "type", None)
        if kind == "function_call":
            call_id = getattr(item, "call_id", None) or getattr(item, "id", None)
            content.append(SimpleNamespace(
                type="tool_use",
                id=str(call_id),
                name=getattr(item, "name", ""),
                input=_parse_arguments(getattr(item, "arguments", "{}")),
            ))
        elif kind == "message":
            for part in getattr(item, "content", []) or []:
                if getattr(part, "type", None) == "output_text":
                    text = getattr(part, "text", "")
                    if text:
                        content.append(SimpleNamespace(type="text", text=text))

    if not content and getattr(response, "output_text", ""):
        content.append(SimpleNamespace(type="text", text=response.output_text))

    stop_reason = "tool_use" if any(getattr(block, "type", None) == "tool_use" for block in content) else "end_turn"
    incomplete = getattr(response, "incomplete_details", None)
    if getattr(response, "status", None) == "incomplete" and getattr(incomplete, "reason", None) == "max_output_tokens":
        stop_reason = "max_tokens"
    return SimpleNamespace(content=content, stop_reason=stop_reason)


def openai_messages_create(*, model: str | None = None, system: str = "", messages: list | None = None,
                           tools: list | None = None, max_tokens: int = 8000, **_):
    request = {
        "model": model or MODEL,
        "instructions": system or "",
        "input": _to_openai_input(messages or []),
        "max_output_tokens": max_tokens,
    }
    openai_tools = _to_openai_tools(tools)
    if openai_tools:
        request["tools"] = openai_tools
    return _from_openai_response(client.responses.create(**request))


SYSTEM = f"You are a coding agent at {WORKDIR}. All destructive operations require user approval."


# ═══════════════════════════════════════════════════════════
#  FROM s02 (unchanged): Tool Implementations
# ═══════════════════════════════════════════════════════════

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    try:
        r = subprocess.run(command, shell=True, cwd=WORKDIR,
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


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
#  FROM s02 (unchanged): Tool Definitions & Dispatch
# ═══════════════════════════════════════════════════════════

TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to a file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in a file once.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
    {"name": "glob", "description": "Find files matching a glob pattern.",
     "input_schema": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}},
]

TOOL_HANDLERS = {
    "bash": run_bash, "read_file": run_read, "write_file": run_write,
    "edit_file": run_edit, "glob": run_glob,
}


# ═══════════════════════════════════════════════════════════
#  NEW in s03: Three-Gate Permission Pipeline
# ═══════════════════════════════════════════════════════════

# Gate 1: Hard deny list — always forbidden
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

def check_deny_list(command: str) -> str | None:
    for pattern in DENY_LIST:
        if pattern in command:
            return f"Blocked: '{pattern}' is on the deny list"
    return None


# Gate 2: Rule matching — context-dependent checks
PERMISSION_RULES = [
    {"tools": ["write_file", "edit_file"],
     "check": lambda args: not (WORKDIR / args.get("path", "")).resolve().is_relative_to(WORKDIR),
     "message": "Writing outside workspace"},
    {"tools": ["bash"],
     "check": lambda args: any(kw in args.get("command", "") for kw in ["rm ", "> /etc/", "chmod 777"]),
     "message": "Potentially destructive command"},
]

def check_rules(tool_name: str, args: dict) -> str | None:
    for rule in PERMISSION_RULES:
        if tool_name in rule["tools"] and rule["check"](args):
            return rule["message"]
    return None


# Gate 3: User approval — wait for confirmation after rule match
def ask_user(tool_name: str, args: dict, reason: str) -> str:
    print(f"\n\033[33m⚠  {reason}\033[0m")
    print(f"   Tool: {tool_name}({args})")
    choice = input("   Allow? [y/N] ").strip().lower()
    return "allow" if choice in ("y", "yes") else "deny"


# Pipeline: all three gates chained
def check_permission(block) -> bool:
    if block.name == "bash":
        reason = check_deny_list(block.input.get("command", ""))
        if reason:
            print(f"\n\033[31m⛔ {reason}\033[0m")
            return False
    reason = check_rules(block.name, block.input)
    if reason:
        decision = ask_user(block.name, block.input, reason)
        if decision == "deny":
            return False
    return True


# ═══════════════════════════════════════════════════════════
#  agent_loop — same as s02, with check_permission() inserted
# ═══════════════════════════════════════════════════════════

def agent_loop(messages: list):
    while True:
        response = openai_messages_create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\033[36m> {block.name}\033[0m")

            # s03 change: run through permission pipeline before executing
            if not check_permission(block):
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": "Permission denied."})
                continue

            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else f"Unknown: {block.name}"
            print(str(output)[:200])
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})

        messages.append({"role": "user", "content": results})


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
        agent_loop(history)
        for block in history[-1]["content"]:
            if getattr(block, "type", None) == "text":
                print(block.text)
        print()
