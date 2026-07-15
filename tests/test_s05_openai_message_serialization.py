import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAI_MODULES = [
    ("s03", REPO_ROOT / "s03_permission" / "code_openai.py"),
    ("s04", REPO_ROOT / "s04_hooks" / "code_openai.py"),
    ("s05", REPO_ROOT / "s05_todo_write" / "code_openai.py"),
]


def load_openai_module(module_name: str, module_path: Path, temp_cwd: Path):
    fake_openai = types.ModuleType("openai")
    fake_dotenv = types.ModuleType("dotenv")

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            self.responses = types.SimpleNamespace(create=None)

    setattr(fake_openai, "OpenAI", FakeOpenAI)
    setattr(fake_dotenv, "load_dotenv", lambda override=True: None)

    previous_modules = {
        "openai": sys.modules.get("openai"),
        "dotenv": sys.modules.get("dotenv"),
    }
    previous_cwd = Path.cwd()
    previous_model = os.environ.get("OPENAI_MODEL")

    spec = importlib.util.spec_from_file_location(
        f"{module_name}_openai_serialization_test",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)

    sys.modules["openai"] = fake_openai
    sys.modules["dotenv"] = fake_dotenv
    try:
        os.chdir(temp_cwd)
        os.environ["OPENAI_MODEL"] = "test-model"
        spec.loader.exec_module(module)
        return module
    finally:
        os.chdir(previous_cwd)
        if previous_model is None:
            os.environ.pop("OPENAI_MODEL", None)
        else:
            os.environ["OPENAI_MODEL"] = previous_model
        for name, previous in previous_modules.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


class FakeFunctionCall:
    type = "function_call"
    name = "bash"
    call_id = "call_1"
    arguments = json.dumps({"command": "echo ok"})

    def model_dump(self, exclude_unset=True, mode="json"):
        return {
            "type": self.type,
            "name": self.name,
            "call_id": self.call_id,
            "arguments": self.arguments,
        }


class FakeResponse:
    def __init__(self, output):
        self.output = output
        self.output_text = ""


class RecordingResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return FakeResponse([FakeFunctionCall()])

        bad_items = [
            item for item in kwargs["input"]
            if not isinstance(item, dict)
        ]
        if bad_items:
            raise AssertionError(f"Non-dict input items sent to OpenAI: {bad_items!r}")
        return FakeResponse([])


class OpenAIMessageSerializationTests(unittest.TestCase):
    def test_agent_loop_converts_function_calls_before_reusing_messages(self):
        for module_name, module_path in OPENAI_MODULES:
            with self.subTest(module=module_name), tempfile.TemporaryDirectory() as tmp:
                module = load_openai_module(module_name, module_path, Path(tmp))
                responses = RecordingResponses()
                module.client = types.SimpleNamespace(responses=responses)
                module.TOOL_HANDLERS["bash"] = lambda command: "ok"

                history = [{"role": "user", "content": "Plan and inspect"}]
                module.agent_loop(history)

                self.assertEqual(len(responses.calls), 2)
                self.assertTrue(all(isinstance(item, dict) for item in history))


if __name__ == "__main__":
    unittest.main()
