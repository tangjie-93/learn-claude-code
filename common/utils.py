"""纯工具函数 — 无模块级状态依赖。"""

import ast
import json


def parse_arguments(raw) -> dict:
    """解析 OpenAI Responses API 函数调用的参数，保证返回 dict。"""
    try:
        parsed = json.loads(raw or "{}") if isinstance(raw, str) else raw
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def function_calls(response):
    """从 Responses API 响应中筛选出所有 function_call 项。"""
    return [
        item
        for item in response.output
        if getattr(item, "type", None) == "function_call"
    ]


def call_args(call) -> dict:
    """便捷封装：返回函数调用的解析后参数。"""
    return parse_arguments(call.arguments)


def as_input_item(item):
    """将 OpenAI SDK 响应对象转为普通 dict，供下一轮请求使用（避免序列化报错）。"""
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_unset=True, mode="json")
    return item


def extract_text(content) -> str:
    """从 OpenAI Responses SDK 对象、dict 或 list 中提取可打印文本。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        content_type = content.get("type")
        if content_type in ("output_text", "text"):
            return content.get("text", "")
        if "content" in content:
            return extract_text(content["content"])
        if "output" in content:
            return extract_text(content["output"])
        return ""

    if getattr(content, "output_text", None):
        return content.output_text

    if getattr(content, "output", None) is not None:
        return extract_text(content.output)

    if isinstance(content, list):
        parts = []
        for item in content:
            item_type = item.get("type") if isinstance(item, dict) else getattr(item, "type", None)
            if item_type in ("output_text", "text"):
                parts.append(item.get("text", "") if isinstance(item, dict) else getattr(item, "text", ""))
            elif item_type == "message":
                parts.append(
                    extract_text(item.get("content", []))
                    if isinstance(item, dict)
                    else extract_text(getattr(item, "content", []))
                )
        return "\n".join(parts)

    return ""


def _normalize_todos(todos):
    """校验并标准化 todo 输入，返回 (任务列表, 错误信息)。"""
    # LLM 可能传 JSON 字符串、Python 字面量字符串或 list，都要兜底
    if isinstance(todos, str):
        try:
            todos = json.loads(todos)
        except json.JSONDecodeError:
            try:
                todos = ast.literal_eval(todos)  # 安全解析 Python 字面量
            except (SyntaxError, ValueError):
                return None, "Error: todos must be a list or JSON array string"
    if not isinstance(todos, list):
        return None, "Error: todos must be a list"
    # 逐项校验：每个元素必须是 dict，且含 content、status 字段
    for i, t in enumerate(todos):
        if not isinstance(t, dict):
            return None, f"Error: todos[{i}] must be an object"
        if "content" not in t or "status" not in t:
            return None, f"Error: todos[{i}] missing 'content' or 'status'"
        if t["status"] not in ("pending", "in_progress", "completed"):
            return None, f"Error: todos[{i}] has invalid status '{t['status']}'"
    return todos, None
