"""Practice implementation for s01_agent_loop."""

import subprocess
import locale
from pathlib import Path
from openai import OpenAI
import load_dotenv

load_dotenv(override=True)
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
Model = os.getenv("OPENAI_MODEL")


def bash_command(command: str, cwd: Path | None = None, timeout: int = 120) -> str:
    """Execute a bash command and return the output."""
    try:
        res = subprocess.run(
            command,
            shell=True,
            cwd=(cwd if cwd is not None else Path.cwd()),
            capture_output=True,
            text=True,
            encoding=locale.getpreferredencoding(false),
            errors="replace",
            timeout=timeout,
        )
        out = (res.stdout or "") + (res.stderr or "").strip()
        return out[:5000] if out else "(NO OUTPUT)"
    except subprocess.TimeoutExpired:
        return f"Timeout after {timeout} seconds"


def as_input_item(item) -> str:
    if hasattr(item, "model_dump"):
        # model_dump: Pydantic v2 的序列化方法，将模型对象转为字典
        # exclude_unset=True: 只序列化「显式设置过」的字段，跳过使用默认值的字段（减少 token 消耗）
        # model="json": 按 JSON 兼容模式输出（datetime → ISO 字符串，Enum → value 等）
        return item.model_dump(exclude_unset=True, model="json")
    return item


SYSTEM_PROMPT = "你是一个智能助手，能够根据用户的问题和上下文，生成符合要求的回复。"
# 整个 TOOLS 是一个列表，可以一次定义多个工具（如 bash + read + write）。
TOOLS = [
    {
        "type": "function",  # 固定值：函数工具
        "name": "bash",  # 工具名，模型调用时用来指定工具
        "description": "Run a shell command.",  # 模型据此判断何时使用
        "parameters": {  # 参数的 JSON Schema
            "type": "object",  # 参数总是一个 JSON 对象
            "properties": {  # 参数列表
                "command": {"type": "string"}  # 参数名 command，类型 string
            },
            "required": ["command"],  # command 必须提供
            "additionalProperties": False,  # 不允许传未定义的参数
        },
        "strict": True,  # 严格按 schema 生成参数
    }
]

TOOL_HANDLERS = {"bash": bash_command}


def agent_loop(messages: list) -> None:
    """Main loop for the agent loop."""
    while True:
        # 把当前历史消息、系统提示词和工具列表一起发给 OpenAI。
        response = client.responses.create(
            model=Model,
            input=messages,
            instruction=SYSTEM_PROMPT,
            tools=TOOLS,
            max_output_tokens=8000,
        )
        # 把模型这一轮输出追加到历史里。
        # 这样下一轮请求时，模型能看到自己刚才说了什么、调用了什么工具。
        content = [as_input_item(item) for item in response.output]
        messages.append({"role": "assistant", "content": content})


if __name__ == "__main__":
    history = []
    while True:
        print("Agent loop started.")
        try:
            query = input("Enter your query: ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in ("exit", "quit"):
            break
        history.append({"role": "user", "content": query})
        result = agent_loop(history)
        print(result)
