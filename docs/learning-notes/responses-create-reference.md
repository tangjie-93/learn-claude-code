# `client.responses.create()` 入参 & 出参详解

> 源码位置：[s01_agent_loop/code_openai.py#L125-L131](file:///Users/james/Desktop/learn-claude-code/s01_agent_loop/code_openai.py#L125-L131)

---

## 一、实际调用

```python
response = client.responses.create(
    model=MODEL,              # "gpt-5.5"
    instructions=SYSTEM,      # 系统提示词（见 §1.2）
    input=messages,           # 对话历史（见 §1.3）
    tools=TOOLS,              # 工具列表（见 §1.4）
    max_output_tokens=8000,   # 模型输出上限
)
```

---

## 二、入参详情

### 1.1 `model` — 模型名

| 属性 | 值 |
|---|---|
| 类型 | `str` |
| 必填 | 是 |
| 来源 | `os.getenv("OPENAI_MODEL", "gpt-5.5")` |

```python
# 代码出处（s01_agent_loop/code_openai.py L65）
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
```

支持任何 OpenAI 兼容模型：
- `gpt-5.5` — 默认
- `gpt-4o`、`gpt-4o-mini`
- `o3`、`o4-mini`
- 其他兼容 API 的模型（如 DeepSeek 等）

**作用：** 告诉 OpenAI 用哪个模型来处理这次请求。

---

### 1.2 `instructions` — 系统提示词

| 属性 | 值 |
|---|---|
| 类型 | `str` |
| 必填 | 是 |
| 来源 | 硬编码的 `SYSTEM` 字符串 |

```python
# 代码出处（s01_agent_loop/code_openai.py L70-L86）
SYSTEM = (
    "You are a coding agent. "
    "Use the bash tool to inspect repos, run scripts, and work with files. "
    "You can use the following tools to complete tasks. "
    ...
)
```

**作用：**
- 定义 Agent 的身份（"你是一个 coding agent"）
- 给模型行为指令（"用 bash 工具来检查仓库、运行脚本"）
- 约束输出风格

**最佳实践：** `instructions` 应该简明扼要，不超过模型的理解范围，否则效果变差。

---

### 1.3 `input` — 对话历史

| 属性 | 值 |
|---|---|
| 类型 | `list[dict]` 或 `str` |
| 必填 | 是 |
| 来源 | 函数参数 `messages` |

格式：

```python
[
    {"role": "user",     "content": "帮我列出当前目录文件"},
    {"role": "assistant", "content": "好的，我来执行 ls"},
    {"type": "function_call", "call_id": "xx", "name": "bash",
     "arguments": '{"command": "ls -la"}'},
    {"type": "function_call_output", "call_id": "xx",
     "output": "file1.txt\nfile2.txt"},
]
```

**两种消息格式：**

| 格式 | 示例 | 用途 |
|---|---|---|
| 纯文本消息 | `{"role": "user", "content": "..."}` | 普通对话（用户/助手） |
| 工具相关 | `{"type": "function_call", ...}` | 工具调用 |
| 工具结果 | `{"type": "function_call_output", ...}` | 工具执行结果 |

**作用：** 告诉模型"之前发生了什么"，是模型唯一的上下文窗口。

---

### 1.4 `tools` — 工具列表

| 属性 | 值 |
|---|---|
| 类型 | `list[dict]` |
| 必填 | 否（但不传就没工具用） |
| 来源 | 硬编码的 `TOOLS` 列表 |

```python
# 代码出处（s01_agent_loop/code_openai.py L91-L116）
TOOLS = [{
    "type": "function",
    "name": "bash",
    "description": "Run a shell command.",
    "parameters": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
        "additionalProperties": False,
    },
    "strict": True,
}]
```

**`tools` 中的每个元素（工具定义）：**

| 字段 | 类型 | 必填 | 含义 |
|---|---|---|---|
| `type` | `"function"` | 是 | 固定值，OpenAI 只支持 `"function"` |
| `name` | `str` | 是 | 工具名，模型用它来指定调哪个工具 |
| `description` | `str` | 是 | 自然语言描述，**模型据此判断何时用这个工具** |
| `parameters` | `dict` | 是 | JSON Schema 格式的参数定义 |
| `parameters.type` | `"object"` | 是 | 固定值 |
| `parameters.properties` | `dict` | 是 | 参数名 → 类型映射 |
| `parameters.required` | `list[str]` | 否 | 必填参数列表 |
| `parameters.additionalProperties` | `bool` | 否 | `False` 阻止模型随意加参数 |
| `strict` | `bool` | 否 | `True` 强制模型严格按 schema 输出 |

**不传 `tools` 会怎样？** 模型就是纯聊天，不会调用任何工具。

---

### 1.5 `max_output_tokens` — 输出上限

| 属性 | 值 |
|---|---|
| 类型 | `int` |
| 必填 | 否 |

```python
max_output_tokens=8000,
```

**作用：** 限制模型单次响应的最大 token 数。超过就截断。

**为什么设 8000？**
- 防止模型一次输出过长（token 消耗）导致响应时间过久或费用过高
- 同时确保有足够空间返回工具调用的完整参数和文字回复

---

### 1.6 其他可用参数（代码中未使用但 API 支持）

> 本节列出 `client.responses.create()` **所有可用参数**，包括代码中用到的和未用到的。

#### 全参数速查表

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `model` | `str` | **是** | — | 模型 ID，如 `gpt-5.5`、`gpt-4o` |
| `instructions` | `str` | 否 | — | 系统提示词，定义 Agent 身份和行为 |
| `input` | `str` 或 `list[dict]` | **是** | — | 对话历史或单条用户消息 |
| `tools` | `list[dict]` | 否 | `None` | 工具列表，模型可调用的函数 |
| `max_output_tokens` | `int` | 否 | — | 输出 token 上限 |
| `temperature` | `float` | 否 | `1` | 随机性控制：`0` = 确定，`2` = 最随机 |
| `top_p` | `float` | 否 | `1` | 核采样：只考虑累积概率达 `top_p` 的 token |
| `frequency_penalty` | `float` | 否 | `0` | -2.0 ~ 2.0，正值减少重复词 |
| `presence_penalty` | `float` | 否 | `0` | -2.0 ~ 2.0，正值鼓励新话题 |
| `stop` | `str` 或 `list[str]` | 否 | — | 停止序列，遇到立即停 |
| `stream` | `bool` | 否 | `False` | 是否流式返回 |
| `logprobs` | `bool` | 否 | `False` | 是否返回每个 token 的对数概率 |
| `top_logprobs` | `int` | 否 | — | 返回概率最高的前 N 个 token |
| `logit_bias` | `dict` | 否 | — | 调整特定 token 出现概率（-100 ~ 100） |
| `n` | `int` | 否 | `1` | 返回几个备选回答 |
| `seed` | `int` | 否 | — | 固定随机种子，确保可复现 |
| `response_format` | `dict` | 否 | — | 结构化输出格式（`json_schema` 等） |
| `store` | `bool` | 否 | `False` | 是否存储响应供后续使用 |
| `metadata` | `dict` | 否 | — | 自定义标签，用于 dashboard 过滤 |
| `service_tier` | `str` | 否 | `"auto"` | 服务延迟等级 |
| `user` | `str` | 否 | — | 最终用户标识符，用于监控防滥用 |
| `previous_response_id` | `str` | 否 | — | 上一轮响应的 ID，实现服务端对话管理 |

#### 常用参数分类

**生成行为控制（4 个）：**

| 参数 | 通俗解释 |
|---|---|
| `temperature` | 创意度：`0` = 死板（适合写代码），`2` = 天马行空（适合写小说） |
| `top_p` | 核采样：只从概率最高的 token 中选，间接控制多样性。**和 temperature 二选一** |
| `frequency_penalty` | 防复读：正数让模型少重复已说过的词 |
| `presence_penalty` | 防跑题：正数让模型多提新概念 |

**调试/分析参数（3 个）：**

| 参数 | 用途 |
|---|---|
| `logprobs` | 返回每个 token 的概率，分析模型为什么不自信 |
| `seed` | 固定随机数，同样的输入 + seed = 同样的输出，便于调试 |
| `store` | 存储响应，在 OpenAI Dashboard 中查看历史记录 |

**输出格式参数（2 个）：**

| 参数 | 用途 |
|---|---|
| `response_format` | 强制模型返回 JSON Schema 格式的结构化数据 |
| `stream` | 逐 token 流式返回，实现打字机效果 |

**多轮对话参数（1 个）：**

| 参数 | 用途 |
|---|---|
| `previous_response_id` | 服务端管理对话历史——传上轮 `response.id`，省去手动维护 `messages` |

#### 为什么代码中只用了 5 个参数？

这个 Agent 的设计理念是**简洁可控**：

- 不需要调整随机性（`temperature`、`top_p`）——coding agent 要确定性的输出
- 不需要流式（`stream`）——交互式的命令行场景不适合
- 不需要服务端会话（`previous_response_id`）——手动管理 `messages` 更灵活
- 不需要日志概率（`logprobs`）——不分析模型内部状态

---

## 三、出参（`response` 对象）

### 3.1 整体结构：`output` vs `output_text`

`response` 对象上最常用的两个属性：

| 属性 | 类型 | 含义 |
|---|---|---|
| `response.output` | `list` | 原始输出列表，包含所有类型的 item（文本消息、工具调用等） |
| `response.output_text` | `str` | **便捷属性**：SDK 自动从 `output` 中只提取文本块，合并成一个字符串 |

```python
# 假设模型返回了：
response.output = [
    {"type": "message", "content": [
        {"type": "output_text", "text": "让我检查一下文件。"}
    ]},
    {"type": "function_call", "call_id": "xx",
     "name": "bash", "arguments": '{"command": "ls"}'},
    {"type": "message", "content": [
        {"type": "output_text", "text": "当前目录为空。"}
    ]},
]

# response.output      → 列表，包含 3 个元素（含 function_call）
# response.output_text → "让我检查一下文件。当前目录为空。"  ← 自动跳过 function_call
```

**什么时候用哪个？**

| 场景 | 用 `output` | 用 `output_text` |
|---|---|---|
| 需要判断模型有没有调工具 | ✅ | ❌（拿不到 function_call） |
| 需要遍历所有 content block | ✅ | ❌ |
| 只需要文本回复显示给用户 | ❌ | ✅（一行搞定） |

这就是为什么代码中同时出现了两者：
- `response.output` → 遍历找 function_call（L141-L147）
- `response.output_text` → 直接拿文本显示（L130）

### 3.2 `response.output` — 模型输出列表

类型：`list[OpenAIObject]`

**每个元素可能是：**

#### ① 文本消息

```python
{
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "output_text",
            "text": "当前目录下有 3 个文件：file1.txt ..."
        }
    ]
}
```

#### ② 工具调用（`function_call`）

```python
{
    "type": "function_call",
    "call_id": "call_abc123",      # 唯一调用 ID，回填结果时匹配
    "name": "bash",                 # 工具名
    "arguments": '{"command": "ls -la"}'  # 参数（JSON 字符串）
}
```

### 3.3 代码中如何使用 `response`

```python
# L136: 把模型输出追加到历史
messages.extend(as_input_item(item) for item in response.output)

# L141-L147: 筛选出工具调用
tool_calls = [
    item
    for item in response.output
    if getattr(item, "type", None) == "function_call"
]

# L130: 取文字内容
output_text = response.output_text
```

### 3.4 `response` 对象的其他常用属性

| 属性 | 类型 | 含义 |
|---|---|---|
| `output_text` | `str` | 模型输出的纯文本（合并所有 `output_text` 块） |
| `output` | `list` | 输出列表（含 message、function_call 等） |
| `usage` | `Usage` | Token 用量统计 |
| `usage.input_tokens` | `int` | 输入 token 数 |
| `usage.output_tokens` | `int` | 输出 token 数 |
| `usage.total_tokens` | `int` | 总 token 数 |
| `id` | `str` | 请求的唯一 ID |
| `model` | `str` | 实际使用的模型 |
| `status` | `str` | `"completed"` / `"failed"` 等 |

---

## 四、一次完整调用的数据流

```
client.responses.create(          →  发送请求
    model="gpt-5.5",                  模型选择
    instructions="You are ...",       系统 prompt
    input=[历史消息],                  对话历史
    tools=[工具定义],                  工具定义
    max_output_tokens=8000            输出限制
)

↓ 返回 response

response.output = [
    {"type": "message", "role": "assistant",          ← 模型说的文字
     "content": [{"type": "output_text", "text": "我来帮你..."}]},
    {"type": "function_call", "call_id": "xx",        ← 模型要调工具
     "name": "bash", "arguments": '{"command":"ls"}'},
]

↓ 代码处理

1. messages.extend(as_input_item(item) for item in response.output)
   → 把输出全部追加到历史

2. tool_calls = [item for item in response.output
                 if item.type == "function_call"]
   → 筛选出工具调用

3. 如果有 tool_calls → 执行工具 → 回填结果 → 继续循环
   如果没有 tool_calls → 返回 response.output_text 给用户
```

---

## 五、文档来源

| 内容 | 来源 |
|---|---|
| 函数调用 | [OpenAI Responses API 文档](https://platform.openai.com/docs/api-reference/responses/create) |
| 工具定义 schema | [OpenAI Function Calling 指南](https://platform.openai.com/docs/guides/function-calling) |
| 代码中用法 | `s01_agent_loop/code_openai.py` |
