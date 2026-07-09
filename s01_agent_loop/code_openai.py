#!/usr/bin/env python3
"""
s01_agent_loop_openai.py - The Agent Loop with OpenAI

Same harness shape as code.py, but using OpenAI's Responses API:

    while tool_calls:
        response = LLM(messages, tools)
        execute tools
        append function_call_output

Usage:
    pip install openai python-dotenv
    OPENAI_API_KEY=... OPENAI_MODEL=gpt-5.5 python s01_agent_loop/code_openai.py
"""

import json
import os
import subprocess

try:
    import readline
    # macOS 的 libedit 在处理中文输入时有退格问题，这四行修复它
    readline.parse_and_bind("set bind-tty-special-chars off")
    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set output-meta on")
    readline.parse_and_bind("set convert-meta off")
except ImportError:
    pass

from dotenv import load_dotenv
from openai import OpenAI
#  override=True ： .env 文件里的值 会强制覆盖 系统中已有的同名环境变量。即 .env 文件的优先级更高。
load_dotenv(override=True)

client_kwargs = {}
if os.getenv("OPENAI_BASE_URL"):
    client_kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]

client = OpenAI(**client_kwargs)
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

# -- Tool（工具）定义 -----------------------------------------------------------
# 告诉 OpenAI："你可以调用这个工具来做事"，就像给模型一本说明书。
# 格式是 OpenAI Function Calling API 规定的，字段名不能随便改。
TOOLS = [{
    # type: 固定值 "function"，表示这是一个函数类型的工具
    "type": "function",
    # name: 给工具取个名字，模型调用时会用这个名字
    "name": "bash",
    # description: 用自然语言告诉模型这工具是干嘛的，模型据此判断什么时候用它
    "description": "Run a shell command.",
    # parameters: 工具的"参数表"——告诉模型这个函数接受什么输入
    "parameters": {
        "type": "object",             # 固定写法：参数总是一个 JSON 对象
        "properties": {               # 定义有哪些参数，每个参数的类型
            "command": {"type": "string"}  # 一个叫 command 的参数，类型是字符串
        },
        "required": ["command"],      # command 是必填的，不填模型会报错
        "additionalProperties": False,  # 不允许模型塞额外参数，防止它乱传
    },
    # strict: 要求模型严格按上面的 schema 生成参数，不能自由发挥
    "strict": True,
}]


# -- Tool execution ----------------------------------------------------------
def run_bash(command: str) -> str:
    """执行一条 bash 命令，并把命令输出作为字符串返回。"""
    # 这里先做一层非常粗的安全拦截，避免模型执行明显危险的系统命令。
    # 注意：这只是教学 demo 的简化保护，不是真正完整的权限系统。
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        # shell=True: 允许执行完整的 shell 命令，如 "ls -la"
        # cwd=os.getcwd(): 命令在当前项目目录执行
        # capture_output=True: 截获命令输出存到 r.stdout/r.stderr，代码才能拿到并处理
        # text=True: 输出自动解码为普通字符串（不加的话是 bytes，后面拼字符串会报错）
        # timeout=120: 最多等 120 秒，防止命令卡死
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        # 合并正常输出和错误输出，一起返回给模型
        out = (r.stdout + r.stderr).strip()
        # 输出太长会撑爆上下文，所以最多保留前 50000 个字符。
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        # 命令超时后，把错误信息作为工具结果返回给模型。
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        # 系统层面执行失败时，也把错误信息返回给模型。
        return f"Error: {e}"


def parse_arguments(raw: str) -> dict:
    """把模型传来的 JSON 参数字符串解析成 Python 字典。"""
    try:
        # OpenAI 的工具参数是 JSON 字符串，例如 '{"command": "ls"}'。
        # json.loads 会把它变成 Python 字典：{"command": "ls"}。
        return json.loads(raw or "{}")
    except json.JSONDecodeError as e:
        # 如果模型传来的 JSON 格式坏了，不让程序崩溃，而是把错误包装成字典返回。
        return {"_error": f"Invalid JSON arguments: {e}"}


def as_input_item(item):
    """把 OpenAI SDK 的响应对象转换成下一轮请求可接收的普通 dict。"""
    # response.output 里通常是 SDK 对象，不一定能直接放回下一轮 input。
    # model_dump 会把它转成普通 JSON 风格数据，方便继续对话。
    if hasattr(item, "model_dump"):
        # exclude_unset=True ： 不包含 None 值的字段。
        # mode="json" ： 以 JSON 格式输出。
        return item.model_dump(exclude_unset=True, mode="json")
    # 如果 item 已经是普通 dict 或字符串，就原样返回。
    return item


# -- The core pattern: call tools until the model stops ----------------------
def agent_loop(messages: list):
    """核心 Agent 循环：调用模型、执行工具、回填结果，直到模型停止调用工具。"""
    while True:
        # 把当前历史消息、系统提示词和工具列表一起发给 OpenAI。
        # 模型会决定：直接回答，还是调用我们提供的 bash 工具。
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM,
            input=messages,
            tools=TOOLS,
            max_output_tokens=8000,
        )

        # Append assistant turn
        # 把模型这一轮输出追加到历史里。
        # 这样下一轮请求时，模型能看到自己刚才说了什么、调用了什么工具。
        messages.extend(as_input_item(item) for item in response.output)

        # If the model didn't call a tool, we're done
        # 找出模型这一轮里所有的工具调用。
        # 在 OpenAI Responses API 中，工具调用的类型是 "function_call"。
        tool_calls = [
            item for item in response.output
            # 只取类型为 "function_call" 的项。
            if getattr(item, "type", None) == "function_call"
        ]
        if not tool_calls:
            # 没有工具调用，说明模型已经给出最终回答，循环结束。
            return response

        # Execute each tool call, collect results
        # 模型一次可能请求多个工具调用，这里逐个执行。
        for call in tool_calls:
            # call.arguments 是 JSON 字符串，先解析成 Python 字典。
            args = parse_arguments(call.arguments)
            if call.name != "bash":
                # 目前我们只注册了 bash 工具，其他工具名都视为未知工具。
                output = f"Error: Unknown tool {call.name}"
            elif "_error" in args:
                # 参数 JSON 解析失败，把错误直接作为工具输出返回给模型。
                output = args["_error"]
            else:
                # 取出模型想执行的 shell 命令。
                command = args.get("command", "")
                #  黄色打印命令
                print(f"\033[33m$ {command}\033[0m")
                # 真正执行命令，并拿到命令输出。
                output = run_bash(command)
                # 为了命令行界面不刷屏，只预览前 200 个字符。
                print(output[:200])

            # 把工具执行结果追加到消息历史里。
            # call_id 必须和模型刚才的工具调用对应上，模型才知道这是哪次调用的结果。
            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output,
            })


# -- Entry point -------------------------------------------------------------
if __name__ == "__main__":
    print("s01: Agent Loop (OpenAI)")
    print("输入问题，回车发送。输入 q 退出。\n")

    history = []
    while True:
        try:
            query = input("\033[36ms01-openai >> \033[0m")  # 显示青色提示符，等待用户输入，返回输入的字符串
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        response = agent_loop(history)
        if getattr(response, "output_text", ""):
            print(response.output_text)
        # 换行，方便下一次输入
        print()
