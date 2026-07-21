# Day 19 学习记录

## 1. 今天学习的文件

- `s11_error_recovery/code_openai.py` -- 三层错误恢复机制

## 2. 核心概念

**错误恢复不是"吞掉错误"，而是给系统自愈的能力。**

| 错误类型 | 恢复策略 | 最多重试 | 原理 |
|---|---|---|---|
| `max_output_tokens` (输出被截断) | 升级 8K→64K → continuation prompt | escalate 1 次 + continue 3 次 | 给更多空间，还不够就让模型接着写 |
| `prompt_too_long` (输入过长) | reactive compact → 重试 | 1 次 | 裁剪旧消息，只保留尾部 |
| `429` (限流) | 指数退避 + 随机抖动 | 10 次 | 等服务器恢复 |
| `529` (过载) | 指数退避 + 连续 3 次切备用模型 | 10 次 | 等服务器恢复，不行就换模型 |
| 其他错误 | 记日志，返回错误消息 | 0 | 非瞬态，不重试 |

**关键设计原则**：
- 错误分"瞬态"和"非瞬态"——429/529 可能自己恢复，可以重试；`prompt_too_long` 不会自己好，需要主动压缩
- `RecoveryState` 跨循环跟踪状态，防止无限重试（escalate 只一次，compact 只一次）
- jitter 防止惊群效应（thundering herd）

## 3. 关键代码

> 以下源码来自 [s11_error_recovery/code_openai.py](file:///Users/james/Desktop/learn-claude-code/s11_error_recovery/code_openai.py)

### 3.1 恢复状态追踪：`RecoveryState`

```python
class RecoveryState:
    """跟踪错误恢复状态：是否已升级 token、已执行 reactive compact、连续 529 次数、当前模型。"""
    def __init__(self):
        self.has_escalated = False                  # 只允许升级 token 一次
        self.recovery_count = 0                     # continuation prompt 次数
        self.consecutive_529 = 0                    # 连续 529 计数器
        self.has_attempted_reactive_compact = False # 只允许 compact 一次
        self.current_model = PRIMARY_MODEL           # 当前使用的模型（切备胎后会变）
```

### 3.2 指数退避 + 抖动：`retry_delay`

```python
def retry_delay(attempt, retry_after=None):
    """指数退避 + 随机抖动，避免惊群效应。如果有 Retry-After 头则直接使用。"""
    if retry_after:
        return retry_after
    base = min(BASE_DELAY_MS * (2 ** attempt), 32000) / 1000  # 0.5s → 1s → 2s → ... 封顶 32s
    jitter = random.uniform(0, base * 0.25)                    # [0, base*25%] 随机抖动
    return base + jitter
```

为什么需要 jitter？假设 1000 个客户端同时遇到 429，没有抖动就全部等 2s 后同时重试 → 服务器又炸（惊群效应）。加上随机抖动后请求分散在 2s~2.5s 之间，压力平滑。

### 3.3 重试包装器：`with_retry`

```python
def with_retry(fn, state: RecoveryState):
    """指数退避重试包装器。处理 429（限流）和 529（过载），连续 529 达阈值时切备用模型。"""
    for attempt in range(MAX_RETRIES):
        try:
            result = fn()
            state.consecutive_529 = 0
            return result
        except Exception as e:
            # 429 → 按 attempt 等指数退避
            if "ratelimit" in str(e).lower() or "429" in str(e):
                time.sleep(retry_delay(attempt))
                continue

            # 529 → 连续 3 次切 FALLBACK_MODEL
            if "overloaded" in str(e).lower() or "529" in str(e):
                state.consecutive_529 += 1
                if state.consecutive_529 >= 3 and FALLBACK_MODEL:
                    state.current_model = FALLBACK_MODEL
                time.sleep(retry_delay(attempt))
                continue

            # 非瞬态 → 向外层抛出
            raise
```

关键点：只重试**瞬态**错误（429/529 过一会儿可能恢复），非瞬态错误直接向外抛给 `agent_loop` 的 try/except 处理。

### 3.4 错误分类器：`is_prompt_too_long_error`

```python
def is_prompt_too_long_error(e: Exception) -> bool:
    """判断 API 错误是否为 prompt/上下文过长（关键词匹配）。"""
    msg = str(e).lower()
    return ("prompt_too_long" in msg        # Anthropic
            or "context_length_exceeded" in msg  # OpenAI
            or ("prompt" in msg and "long" in msg))
```

用关键词匹配而不是错误码——不同 API 的报错格式不统一，关键词匹配更通用。

### 3.5 Path 1：max_tokens 恢复

```python
# 第一阶段：首次触发 → 升级 8K → 64K，不保存截断输出，直接重试
if not state.has_escalated:
    max_tokens = ESCALATED_MAX_TOKENS  # 64000
    state.has_escalated = True
    continue  # ← 同一请求用更大 token 上限重来

# 第二阶段：64K 还是不够 → 保存已输出 + 追加续写提示
messages.extend(as_input_item(item) for item in response.output)
if state.recovery_count < MAX_RECOVERY_RETRIES:  # 最多 3 次
    messages.append({"role": "user", "content": CONTINUATION_PROMPT})
    continue
```

`CONTINUATION_PROMPT = "Output token limit hit. Resume directly — no apology, no recap. Pick up mid-thought."`

### 3.6 Path 2：prompt_too_long 恢复

```python
except Exception as e:
    if is_prompt_too_long_error(e):
        if not state.has_attempted_reactive_compact:
            messages[:] = reactive_compact(messages)  # 只保留尾部 5 条
            state.has_attempted_reactive_compact = True
            continue
        # compact 后还是太长 → 放弃
        return
```

### 3.7 reactive_compact

```python
def reactive_compact(messages: list) -> list:
    """应急压缩：保留尾部 5 条消息。真 CC 会用 LLM 生成摘要，教学版直接裁剪。"""
    tail = messages[-5:]
    return [{"role": "user",
             "content": "[Reactive compact] Earlier conversation trimmed. "
                        "Continue from where you left off."}, *tail]
```

### 3.8 agent_loop 中的使用

```python
def agent_loop(messages: list, context: dict):
    while True:
        try:
            # with_retry 自动处理 429/529
            response = with_retry(lambda: client.responses.create(...), state)
        except Exception as e:
            # with_retry 抛出的非瞬态错误 → Path 2 检查 prompt_too_long
            if is_prompt_too_long_error(e):
                messages[:] = reactive_compact(messages)
                continue
            return  # 不可恢复

        # Path 1: 正常响应但被截断
        if response.status == "incomplete":
            # escalate → continue prompt 逻辑
            ...

        # 正常流程
        ...
```

## 4. 我理解的流程

```mermaid
flowchart TD
    A["agent_loop 入口"] --> B["with_retry 包装 LLM 调用"]
    
    B --> C{"LLM 调用结果？"}
    
    C -- 成功 --> D{"status == incomplete?"}
    D -- 否 --> E["正常流程：\n追加 assistant → 工具执行 → 循环"]
    D -- 是 --> F{"已 escalate 过？"}
    F -- 否 --> G["升级 max_tokens=64K\nhas_escalated=True\n不保存截断输出，重试"]
    G --> B
    F -- 是 --> H{"recovery_count < 3?"}
    H -- 是 --> I["保存截断输出\n追加 CONTINUATION_PROMPT\nrecovery_count++"]
    I --> B
    H -- 否 --> J["放弃，返回"]
    
    C -- 失败 --> K{"429 或 529?"}
    K -- 是 --> L["with_retry 内部：\n指数退避 + 抖动重试\n连续 529 切备用模型"]
    L --> B
    
    K -- 否 --> M{"prompt_too_long?"}
    M -- 是 --> N{"已 compact 过？"}
    N -- 否 --> O["reactive_compact:\n保留尾部 5 条\nhas_attempted = True"]
    O --> B
    N -- 是 --> P["放弃，返回错误"]
    
    M -- 否 --> Q["非瞬态错误\n放弃，返回错误"]
```

## 5. 仍然不清楚的问题

- `with_retry` 的 `fn` 参数为什么用 `lambda` 包一层？直接传 `client.responses.create` 不行吗？——因为需要捕获 `max_tokens` 和 `state.current_model` 的当前值，`lambda` 形成了闭包。

## 6. 明天要验证的点

- `s12_task_system` 中任务系统的设计，以及 todo 工具的实现
