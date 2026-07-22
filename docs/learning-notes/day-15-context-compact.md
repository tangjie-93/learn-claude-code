# Day 15 学习记录

## 1. 今天学习的文件

- `s08_context_compact/code_openai.py` -- 四层压缩管线

## 2. 核心概念

**为什么需要上下文压缩？** agent 长时间运行时 `messages` 列表不断膨胀，每轮都要把所有历史发给 LLM，token 消耗和延迟线性增长，最终超出模型上下文窗口。

**核心原则：便宜的先做，贵的最后做。**

四层压缩管线（0 API 调用 → 1 API 调用）：

```
L3 budget → L1 snip → L2 micro → [token > 50000?] → L4 summary → LLM
                                                              ↓ prompt_too_long?
                                                          reactive_compact
```

| 层级 | 名称 | 做什么 | API 调用 | 代价 |
|---|---|---|---|---|
| L3 | `function_call_output_budget` | 大工具输出（>30KB）持久化到磁盘 | 0 | 极低 |
| L1 | `snip_compact` | 消息超过 50 条时裁掉中间消息 | 0 | 极低 |
| L2 | `micro_compact` | 旧工具输出（>120 字符）替换为占位符，只保留最近 2 个 | 0 | 极低 |
| L4 | `compact_history` | LLM 摘要全文 → 替换为一条摘要消息 | 1 | 昂贵 |
| Emergency | `reactive_compact` | API 仍报 `prompt_too_long` → 存档 + 只保留尾部 5 条 | 1 | 最贵 |

**L2 micro_compact vs L4 auto compact（`compact_history`）的区别：**

| | micro_compact (L2) | auto compact / compact_history (L4) |
|---|---|---|
| API 调用 | 0 次 | 1 次（调 LLM 生成摘要） |
| 触发条件 | 无门槛，每轮都执行 | `estimate_size(messages) > 50000` |
| 处理方式 | 旧工具输出文本替换为占位符 | 整段对话交给 LLM 压缩成一段摘要 |
| 效果 | 消息数量不变，体积缩小 | 整段对话变成 **1 条** `[Compacted]` 消息 |
| 代价 | 便宜 | 昂贵（多一次 API 调用） |

**micro_compact 前后（只替换旧工具输出，消息条数不变）：**

压缩前 — 3 个 function_call_output，每个几百行代码：
```
[
  {"role": "user", "content": [
    {"type": "function_call_output", "output": "import os\nimport sys\n...(500行)..."}]},
  {"role": "user", "content": [
    {"type": "function_call_output", "output": "class Foo:\n...(最后2个保留原样)"}]},
  {"role": "user", "content": [
    {"type": "function_call_output", "output": "def bar():\n...(最后2个保留原样)"}]},
]
```
压缩后 — 第 1 个输出变占位符：
```
[
  {"role": "user", "content": [
    {"type": "function_call_output", "output": "[Earlier tool result compacted. Re-run if needed.]"}]},
  ...（后 2 条不变）
]
```

**auto compact 前后（整段对话 → 1 条摘要消息）：**

压缩前：100+ 条 messages，`len(str(msgs)) > 50000`

压缩后：
```
[
  {"role": "user", "content": "[Compacted]\n\n用户正在调试一个 Flask 应用的登录功能，已定位到 bcrypt 版本不兼容的问题..."}
]
```

## 3. 关键代码

**L1 snip_compact 的核心安全逻辑：**

```python
# 防止 function_call 和 function_call_output 被拦腰切断
if head_end > 0 and _message_has_function_call(messages[head_end - 1]):
    while head_end < len(messages) and _is_function_call_output_message(messages[head_end]):
        head_end += 1  # 把配对的 output 也拉进保留范围
```

**L4 compact_history 的摘要 prompt 策略：**

```python
"Preserve: 1. current goal, 2. key findings/decisions, 3. files read/changed, "
"4. remaining work, 5. user constraints."
```

**compact 工具的特殊处理**（agent_loop 中 [code_openai.py#L763](file:///Users/james/Desktop/learn-claude-code/s08_context_compact/code_openai.py#L763)）：模型可以主动调用 `compact` 工具来触发 `compact_history`，这是一个"模型自知上下文满了"的主动压缩机制。

## 4. 我理解的流程

```
每轮 agent_loop 开始
  → L3: 工具输出太大的 → 写入磁盘，只留 2000 字符预览
  → L1: 消息超过 50 条 → 保留开头 3 条 + 尾部 47 条，中间裁掉
  → L2: 旧工具输出 → 替换为占位文本
  → 检查 token 是否 > 50000
    → 是 → L4: LLM 摘要全文，对话压缩为一条
    → 否 → 直接调 LLM
  → LLM 调用成功 → 执行工具 → 下一轮
  → LLM 报 prompt_too_long → reactive_compact → 重试一次
```

## 5. 仍然不清楚的问题

- L3 优先于 L1 执行的原因是什么？（文档说顺序是 "budget → snip → micro"，但原因没有明确解释）

## 6. 明天要验证的点

- tests/test_compaction_tool_pairs.py 中 `tool_use/tool_result` 配对保护的边界用例
