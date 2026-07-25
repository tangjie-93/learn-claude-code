from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "s15_agent_teams" / "code_openai.py"


def load_agent_loop():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "agent_loop"
    )
    namespace: dict = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace["agent_loop"]


def test_function_call_output_is_a_top_level_input_item() -> None:
    call = SimpleNamespace(type="function_call", name="tool", call_id="call_1")
    responses = [SimpleNamespace(output=[call]), SimpleNamespace(output=[])]
    requests = []

    def create(**kwargs):
        requests.append(deepcopy(kwargs["input"]))
        return responses.pop(0)

    agent_loop = load_agent_loop()
    agent_loop.__globals__.update(
        {
            "MODEL": "test-model",
            "TOOLS": [],
            "client": SimpleNamespace(responses=SimpleNamespace(create=create)),
            "get_system_prompt": lambda context: "system",
            "consume_cron_queue": lambda: [],
            "as_input_item": lambda item: {
                "type": item.type,
                "name": item.name,
                "call_id": item.call_id,
            },
            "function_calls": lambda response: response.output,
            "call_args": lambda block: {},
            "should_run_background": lambda name, arguments: False,
            "execute_tool": lambda block: "done",
            "collect_background_results": lambda: [],
            "update_context": lambda context, messages: context,
        }
    )

    agent_loop([{"role": "user", "content": "run tool"}], {})

    second_input = requests[1]
    assert any(item.get("type") == "function_call_output" for item in second_input)
    assert not any(
        item.get("role") == "user"
        and isinstance(item.get("content"), list)
        and any(
            block.get("type") == "function_call_output"
            for block in item["content"]
            if isinstance(block, dict)
        )
        for item in second_input
    )
