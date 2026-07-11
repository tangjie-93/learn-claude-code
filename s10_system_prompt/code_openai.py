#!/usr/bin/env python3
"""
s10: System Prompt — Runtime prompt assembly with caching.

Run:  python s10_system_prompt/code.py
Need: pip install openai python-dotenv + .env with OPENAI_API_KEY

Changes from s09:
  - PROMPT_SECTIONS: topic-keyed dict of prompt fragments
  - assemble_system_prompt(context): select + join sections by real state
  - get_system_prompt(context): deterministic cache via json.dumps
  - agent_loop uses get_system_prompt(context) instead of hardcoded SYSTEM

Memory section loads when .memory/MEMORY.md exists (real state, not keywords).
"""

import os, subprocess, json
from pathlib import Path

try:
    import readline
    readline.parse_and_bind('set bind-tty-special-chars off')
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
MEMORY_DIR = WORKDIR / ".memory"
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
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



# ── Prompt Sections ──

PROMPT_SECTIONS = {
    "identity": "You are a coding agent. Act, don't explain.",
    "tools": "Available tools: bash, read_file, write_file.",
    "workspace": f"Working directory: {WORKDIR}",
    "memory": "Relevant memories are injected below when available.",
}


def assemble_system_prompt(context: dict) -> str:
    """Select and join prompt sections based on current context."""
    sections = []

    # Always loaded — identity, tools, workspace
    sections.append(PROMPT_SECTIONS["identity"])
    sections.append(PROMPT_SECTIONS["tools"])
    sections.append(PROMPT_SECTIONS["workspace"])

    # Conditional — memory loaded when MEMORY.md exists and has content
    memories = context.get("memories", "")
    if memories:
        sections.append(f"Relevant memories:\n{memories}")

    return "\n\n".join(sections)


_last_context_key = None
_last_prompt = None


def get_system_prompt(context: dict) -> str:
    """Cache wrapper — reassemble only when context changes.

    Uses json.dumps for deterministic serialization, not Python's hash()
    which has process randomization and fails on nested dicts/lists.
    This cache only avoids redundant string assembly within a process.
    Real Claude Code additionally protects API-level prompt cache via
    stable section ordering and SYSTEM_PROMPT_DYNAMIC_BOUNDARY.
    """
    global _last_context_key, _last_prompt
    key = json.dumps(context, sort_keys=True, ensure_ascii=False, default=str)
    if key == _last_context_key and _last_prompt:
        print("  \033[90m[cache hit] system prompt unchanged\033[0m")
        return _last_prompt
    _last_context_key = key
    _last_prompt = assemble_system_prompt(context)

    loaded = ["identity", "tools", "workspace"]
    if context.get("memories"):
        loaded.append("memory")
    print(f"  \033[32m[assembled] sections: {', '.join(loaded)}\033[0m")
    return _last_prompt


# ── Tools ──

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


TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"},
                                     "limit": {"type": "integer"}},
                      "required": ["path"]}},
    {"name": "write_file", "description": "Write content to a file.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"},
                                     "content": {"type": "string"}},
                      "required": ["path", "content"]}},
]

TOOL_HANDLERS = {"bash": run_bash, "read_file": run_read, "write_file": run_write}


# ── Context ──

def update_context(context: dict, messages: list) -> dict:
    """Derive context from real state: which tools exist, whether memory files exist."""
    memories = ""
    if MEMORY_INDEX.exists():
        content = MEMORY_INDEX.read_text().strip()
        if content:
            memories = content
    return {
        "enabled_tools": list(TOOL_HANDLERS.keys()),
        "workspace": str(WORKDIR),
        "memories": memories,
    }


# ── Agent Loop ──

def agent_loop(messages: list, context: dict):
    """Main loop — uses assembled system prompt instead of hardcoded SYSTEM."""
    system = get_system_prompt(context)
    while True:
        response = openai_messages_create(
            model=MODEL, system=system, messages=messages,
            tools=TOOLS, max_tokens=8000)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"\033[36m> {block.name}\033[0m")
            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else f"Unknown: {block.name}"
            print(str(output)[:200])
            results.append({"type": "tool_result",
                            "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": results})

        # Re-evaluate context and prompt after each tool round
        context = update_context(context, messages)
        system = get_system_prompt(context)


if __name__ == "__main__":
    print("s10: system prompt — runtime assembly")
    print("Enter a question, press Enter to send. Type q to quit. OpenAI version.\n")
    history = []
    context = update_context({}, [])
    while True:
        try:
            query = input("\033[36ms10 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history, context)
        context = update_context(context, history)
        for block in history[-1]["content"]:
            if getattr(block, "type", None) == "text":
                print(block.text)
        print()
