# 学习目标

完成 30 天学习后，应该达到以下水平：

1. 能完整解释一个 `coding agent` 的核心循环。
2. 能设计和实现基本工具系统，包括 `read`、`write`、`edit`、`bash`。
3. 能理解工具调用、工具结果、上下文历史之间的关系。
4. 能实现简单权限拦截和 `hooks`。
5. 能解释 `todo`、`task system`、`background task` 的区别。
6. 能理解 `subagent` 和 `skill` 的边界。
7. 能说明 `context compact` 为什么必须保护 `tool_use/tool_result` 配对。
8. 能读懂 `agents/s_full.py` 的整体结构。
9. 能基于该项目实现一个自己的 `mini coding agent harness`。

## 阶段性目标

### 第 1 周结束

你应该能说明：

- `agent loop` 的最小结构
    本质上就3步；问模型=>有工具就执行工具=>没有工具就结束循环
    ```python
        while True:
            # 把当前历史消息、系统提示词和工具列表一起发给 OpenAI。
            # 1.调用模型
            response = client.responses.create(
                model=MODEL,
                instructions=SYSTEM,
                input=messages,
                tools=TOOLS,
                max_output_tokens=8000,
            )
            # 2.把模型这一轮输出追加到历史里。
            messages.extend(response.output)
            # 3.检查是否有工具调用
            tool_calls = [
                item for item in response.output
                # 只取类型为 "function_call" 的项。
                if getattr(item, "type", None) == "function_call"
            ]
            if not tool_calls:
                # 没有工具调用，说明模型已经给出最终回答，循环结束。
                return response
            # 4.处理工具调用
            for call in tool_calls:
                args = parse_arguments(call.arguments)
                # 5.调用工具
                output = call_tool(call.name, args)
                # 6.把工具结果追加到历史里。
                messages.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": output,
                })

    ```
- `tool_use` 和 `tool_result` 的关系
    `tool_use` 是模型调用工具的请求，`tool_result` 是工具执行结果。就像一个对话回合：**模型问（`tool_use`）->你答（`tool_result`）->模型根据结果继续思考**
    + `tool_use`: 模型说，我想执行一个工具，指令是 `command`。
    + `tool_result`: 工具执行结果。
- 工具系统如何接入模型调用
    给模型传一份工具说明书（`JSON Schema`）格式，模型根据这个说明书调用工具。模型看到说明书后，如果需要执行一个工具，就不再输出文字，而是在响应里标记为 `function_call`，代码监测到后读参数、执行工具、返回结果，最后把结果追加到历史里。代码如下：
    ```python
    {
        "type": "function_call",
        "name": "bash",
        "arguments": {
            "command": "ls -l"
        }
    }
    ```
    说明书主要格式如下：
    ```python
    {
        "type": "function",
        "name": "bash",
        "description": "执行 shell 命令",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令"
                }
            },
            "required": ["command"],      # command 是必填的，不填模型会报错
            "additionalProperties": False,  # 不允许模型塞额外参数，防止它乱传
        },
        # strict: 要求模型严格按上面的 schema 生成参数，不能自由发挥
        "strict": True,
    }
    ```
    模型根据这个说明书调用工具，指令是 `command`。
- 权限和 `hooks` 为什么必须存在
    + 模型可能要求执行危险操作，比如删除文件、修改系统配置等。为了防止模型执行危险操作，必须有权限拦截。
    + `hooks` 提供一种**可插拔的中间件机制**——不修改主循环代码，允许在模型调用工具之前或之后执行自定义代码。比如，在调用工具之前，可以检查模型是否有权限执行这个工具；在调用工具之后，可以记录工具调用日志名，这种安全策略和业务逻辑解耦。

### 第 2 周结束

你应该能说明：

- `todo` 为什么是 agent 的外部工作记忆
    + `todo_write` 本身不做任何实际工作，不能读文件、不能跑命令，只是让 Agent 在动手之前先理清思路。
    + `todo` 不给 Agent 增加任何**执行能力**。它增加的是**规划能力**
    + `todo` 把"任务进展"写在 `API` 对话之外（内存 + 终端打印），让模型通过一个简单的工具调用来读/写当前状态，作为"写在便利贴上的待办清单"持续跟踪，不占用 `token`。

- `subagent` 如何做职责隔离
    + 不同的 `subagent` 负责不同的任务，互不干扰，通过系统提示词来限定行为边界。父代理只负责发任务和收结果，子代理内部的分析过程父代理完全不可见。好处就是：
    + 每个 `subagent` 都有一个独立的上下文历史，互不干扰。
    + 每个 `subagent` 都有一个独立的工具调用权限，不能调用其他 `subagent` 的工具。
    + 每个 `subagent` 都有一个独立的 `todo` 列表，不能查看其他 `subagent` 的 `todo` 列表。
    + 一个子代理出错也不会影响其他子代理的运行。
    + 可以并行启动多个任务
- `skill` 如何把领域知识按需加载
    + 将 `skill` 的 `name` 和 `description` 作为系统提示词的一部分，让模型知道这个 `skill` 的存在。
    + 需要在 `tools` 列表中添加 `skill` 的 `name`，让模型知道这个 `skill` 的存在。
    + 模型调用 `skill` 时，需要提供 `skill` 的 `name` 和参数，随后根据 `name` 和参数调用 `skill` 的函数，再将 `skill` 的内容结果返回给模型。
- 工具、`todo`、`subagent`、`skill` 的职责边界
    + 工具是手脚，`todo` 是便利贴，`subagent` 是外包工人，`skill` 是参考书。

    | 组件 | 做什么 | 不做什么 |
    |---|---|---|
    | 工具（`Tools`） | 执行原子操作（读文件、跑命令、写文件） | 不做逻辑判断，不管理状态 |
    | `todo` | 记录和展示任务列表（进度追踪） | 不执行任何操作，不替代工具 |
    | `subagent` | 独立的子任务执行者（有完整 `agent loop`） | 不管理全局状态，不跨域做事 |
    | `skill` | 注入领域知识（`prompt` 模板） | 不执行操作，不控制流程 |



### 第 3 周结束

你应该能说明：

- 上下文为什么会膨胀
- `compact` 的风险是什么
- `memory` 和 context 的区别
- `system prompt` 在 harness 中承担哪些策略

### 第 4 周结束

你应该能说明：

- `task system` 如何支撑长期任务
- `background task` 和普通工具调用的区别
- agent team 如何通信和协作
- `worktree isolation` 和 `MCP plugin` 解决什么扩展问题
