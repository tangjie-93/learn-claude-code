# Day 16 学习记录

## 1. 今天学习的文件

- `tests/test_compaction_tool_pairs.py` -- 压缩工具配对测试

## 2. 核心概念

**`tool_use/tool_result` 必须成对保留**，不能只裁一个。如果配对断裂，LLM 会看到一个没有结果的工具调用，或者一个没有调用来源的工具结果，导致模型困惑或报错。

测试覆盖了三种压缩场景下的配对保护：

| 测试 | 场景 | 关键断言 |
|---|---|---|
| `test_snip_compact_keeps_head_tool_pair` | 头部保留区域边界处有 tool_use/tool_result 对 | `compacted[2]` 和 `compacted[3]` 是原始的工具对 |
| `test_snip_compact_keeps_tail_tool_pair` | 尾部保留区域的 tool_use/tool_result 对 | 压缩后无孤立的 tool_result |
| `test_reactive_compact_keeps_tail_tool_pair` | reactive_compact 的配对保护 | `compacted[1]` 等于原始的 tool_use 消息 |
| `test_reactive_compact_summarizes_only_old_history` | 摘要只覆盖被裁掉的部分，尾部原文保留 | `captured["messages"]` == `messages[:4]` |
| `test_reactive_compact_summary_excludes_tail_pair_pulled_in` | 配对 straddle 边界时，tool_use 被拉入尾部 | `captured["messages"]` == `messages[:3]` |

**`assert_no_orphan_tool_results` 的检查逻辑：**

```python
# 每条 tool_result 消息的前一条必须是 tool_use 消息
def assert_no_orphan_tool_results(testcase, messages):
    for idx, message in enumerate(messages):
        if has_tool_result(message):
            testcase.assertGreater(idx, 0)                    # 不是第一条
            testcase.assertTrue(message_has_tool_use(messages[idx - 1]))  # 前一条是 tool_use
```

## 3. 关键代码

**边界 straddle 场景（`test_reactive_compact_summary_excludes_tail_pair_pulled_in`）：**

```python
messages = [
    user_text(),           # 0
    assistant_text(),      # 1
    user_text(),           # 2
    tool_use_message(),    # 3 ← 配对的第一半
    tool_result_message(), # 4 ← 配对的第二半（在 tail_start=4 的边界上）
    assistant_text(),      # 5
    ...
]
# reactive_compact 检测到 messages[4] 是 function_call_output
# 且 messages[3] 是 function_call → tail_start 从 4 降为 3
# 结果：摘要覆盖 messages[:3]，原文保留 messages[3:]
```

**三个模块共享同一套测试**（`s08`、`s09`、`s20` 的 snip_compact 和 reactive_compact 都跑同样的用例），用 `load_module` 动态加载并替换 `anthropic`/`dotenv` 为 fake。

## 4. 我理解的流程

```
snip_compact 执行流程:
  1. 消息数 ≤ max_messages? → 直接返回
  2. 计算 head_end=3, tail_start=len-max_messages+3
  3. 检查 head 边界：最后一 head 条是 function_call → 吞入后续 function_call_output
  4. 检查 tail 边界：第一条 tail 是 function_call_output 且前一条是 function_call → 吞入前条
  5. head >= tail? → 不够裁，返回原样
  6. 拼接：[head部分] + [snipped N messages 占位] + [tail部分]
```

## 5. 仍然不清楚的问题

- 暂无

## 6. 明天要验证的点

- s09_memory 中的 memory 读写机制：`.memory/` 下的文件结构、MEMORY.md 索引格式
