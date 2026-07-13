import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPENAI_EXAMPLES = sorted(
    path for path in ROOT.glob("s*_*/code_openai.py")
    if 3 <= int(path.parent.name[1:3]) <= 20
)
COMPATIBILITY_FUNCTIONS = {
    "_to_openai_input",
    "_to_openai_tools",
    "_from_openai_response",
    "openai_messages_create",
}
ANTHROPIC_BLOCK_TYPES = {"tool_use", "tool_result", "input_schema"}


class OpenAINativeExamplesTests(unittest.TestCase):
    def test_openai_examples_use_responses_api_without_compatibility_layers(self):
        self.assertEqual(len(OPENAI_EXAMPLES), 18)

        for path in OPENAI_EXAMPLES:
            with self.subTest(path=path):
                source = path.read_text()
                tree = ast.parse(source)
                functions = {
                    node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                }

                self.assertFalse(functions & COMPATIBILITY_FUNCTIONS)
                self.assertIn("client.responses.create(", source)
                for block_type in ANTHROPIC_BLOCK_TYPES:
                    self.assertNotIn(block_type, source)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Dict):
                        continue
                    values = {
                        key.value: value
                        for key, value in zip(node.keys, node.values)
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    }
                    if (
                        isinstance(values.get("type"), ast.Constant)
                        and values["type"].value == "function_call_output"
                    ):
                        self.assertIn("output", values)
                        self.assertNotIn("content", values)
                self.assertNotIn(
                    '"properties": {"type": "function", "name":', source
                )


if __name__ == "__main__":
    unittest.main()
