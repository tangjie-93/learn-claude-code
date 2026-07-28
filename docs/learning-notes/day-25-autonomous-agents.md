# Day 25 学习记录

## 1. 今天学习的文件

- `s17_autonomous_agents/README.md` -- s17 的教学目标、生命周期和与 s16 的差异。
- `s17_autonomous_agents/code_openai.py` -- OpenAI Responses API 版本的实际实现。

## 2. 本章要解决的问题

s16 中，Lead 创建任务后还要逐个把任务分配给队友。任务数增多时，Lead 会成为调度瓶颈。

s17 的目标是让队友在空闲时主动查看任务板：只要发现一个未被占用、依赖已经满足的任务，就自行认领并恢复工作。Lead 的职责变成：创建任务、启动队友、接收结果和处理异常，而不是手动分派每一项工作。

```text
s16: Lead 创建任务 -> Lead 分配任务 -> Teammate 工作
s17: Lead 创建任务 -> Teammate 自己扫描并认领 -> Teammate 工作
```

## 3. 核心状态机

每个队友线程经历三个阶段：

```text
             有工具调用
    +------------------------+
    |                        v
  WORK --无工具调用--> IDLE --发现任务/消息--> WORK
    |                        |
    | shutdown_request        | 60 秒无任务
    v                        v
                SHUTDOWN -> 向 Lead 发送 summary -> 线程结束
```

| 阶段 | 实际行为 | 主要退出条件 |
|---|---|---|
| WORK | 处理收件箱，调用大模型，执行工具 | 模型没有工具调用、收到关机请求、模型调用失败 |
| IDLE | 每 5 秒检查收件箱和任务板 | 收到消息、认领到任务、收到关机请求、60 秒超时 |
| SHUTDOWN | 汇总队友最后的文本回复，发给 Lead | 发送 `result` 消息后结束线程 |

代码中的 `spawn_teammate_thread()` 创建后台线程；线程内的外层 `while True` 负责 WORK 和 IDLE 的往复。WORK 阶段最多连续调用大模型 10 次，避免单个队友无限工具循环。

## 4. 自动认领不是只通知模型

自动认领的关键代码在 `idle_poll()`：

```python
unclaimed = scan_unclaimed_tasks()
if unclaimed:
    task = unclaimed[0]
    result = claim_task(task["id"], name)
    if "Claimed" in result:
        messages.append({
            "role": "user",
            "content": f"<auto-claimed>Task {task['id']}: "
                       f"{task['subject']}</auto-claimed>",
        })
        return finish_idle("work", f"已认领 {task['subject']!r}")
```

这里有两个独立动作：

1. `claim_task(task["id"], name)` 修改任务文件。`name` 是当前队友的名称，例如 `alice`；函数将 `task.owner` 写为 `alice`，将 `task.status` 写为 `in_progress`，再保存到 `.tasks/task_*.json`。
2. `<auto-claimed>...</auto-claimed>` 被追加到当前队友的 `messages`，让该队友的大模型知道自己已经获得了什么任务。

因此，任务板才是分配事实的来源；注入给大模型的消息只是让模型获得任务上下文。

### 4.1 可认领任务的条件

`scan_unclaimed_tasks()` 只返回同时满足以下条件的任务：

```python
task.get("status") == "pending"
and not task.get("owner")
and can_start(task["id"])
```

`can_start()` 会逐个检查 `blockedBy` 中的任务：依赖文件必须存在，而且状态必须是 `completed`。因此，有依赖不代表任务永远不能开始；依赖完成后，下一次 IDLE 扫描即可发现该任务。

### 4.2 认领人在哪里体现

```python
def claim_task(task_id: str, owner: str = "agent") -> str:
    # ... 检查 pending、owner、依赖
    task.owner = owner
    task.status = "in_progress"
    save_task(task)
```

队友自动认领时传入的是 `name`；如果当前线程是 bob，实际调用就是：

```python
claim_task(task_id, "bob")
```

任务文件会记录：

```json
{
  "status": "in_progress",
  "owner": "bob"
}
```

除了自动认领，队友的大模型也可以主动调用 `claim_task` 工具。`_make_teammate_handlers(name)` 把该工具绑定为：

```python
"claim_task": lambda task_id: claim_task(task_id, owner=name)
```

两种路径都会把当前队友名称写入任务板。

## 5. 收件箱和协议优先级

IDLE 阶段并不是只扫描任务。它先读取自己的邮箱：

```text
IDLE
  -> 先检查 inbox
     -> shutdown_request: 立即回复 shutdown_response 并退出
     -> 普通消息: 注入 messages，返回 WORK
  -> 再扫描任务板
     -> 找到可认领任务: claim，返回 WORK
  -> 无事: 继续等待下一次轮询
```

这个优先级确保 Lead 要求关机时，队友不会先拿一个新任务才响应。WORK 阶段同样会调用 `handle_inbox_message()`，所以关机请求在两个阶段都能处理。

Lead 侧使用 `consume_lead_inbox()` 统一消费邮箱：协议响应通过 `request_id` 关联到 `pending_requests`，普通 `result` 消息则可以进入 Lead 的对话历史，供下一轮大模型调用使用。

## 6. OpenAI Responses API 循环

Lead 与队友都使用以下模式：

```text
messages -> client.responses.create(...) -> response.output
         -> function_calls(response)
         -> TOOL_HANDLERS / sub_handlers
         -> function_call_output
         -> 下一轮 client.responses.create(...)
```

队友调用模型时只传最近 20 条 `messages`：

```python
input=messages[-20:]
```

这限制了消息条数，但没有限制单条工具输出的字符数。`bash` 或 `read_file` 的大输出仍可能让请求体很大。实际运行时应避免把完整 README、大目录列表或大量测试输出反复送回模型。

## 7. 可观测性：控制台和执行日志

当前 `code_openai.py` 在教学版基础上增加了 `trace()`：

```text
Lead/主线程 ...
Teammate/alice/后台线程 ...
Teammate/bob/后台线程 ...
```

日志记录：

- Lead/队友的生命周期事件和工具调用；
- 工具原始返回；
- 大模型的非 `reasoning` 输出；
- IDLE 的轮询次数及结束原因。

日志文件为 `s17_autonomous_agents/s17_execution.log`。每次以脚本方式启动时会清空该文件；如果文件被编辑器独占导致无法写入，代码会切换到带时间戳的备用日志文件，避免日志写入错误中断队友线程。

## 8. 本次实践中观察到的边界

### 8.1 502 不等于回答解析错误

`InternalServerError: 502` 出现在：

```python
client.responses.create(...)
```

模型还没有返回，所以不会进入 `record_model_response()` 或工具调用解析。消息格式不合法通常更可能得到 4xx 错误；502 常见于自定义网关或其上游模型服务不可用、过载。运行日志出现过明确的 `Our servers are currently overloaded`。

不过，巨大的工具输出会增加服务压力，因此仍应限制返回给模型的上下文大小。

### 8.2 Windows shell 差异

`run_bash()` 使用 `shell=True`，在当前 Windows 环境下实际由 Windows shell 执行。模型如果生成 Unix 命令，例如 `head`，会得到“不是内部或外部命令”。

当前 `run_bash()` 将 stdout 和 stderr 合并成普通字符串；即使命令返回非零退出码，调用方也可能把它显示为“bash 完成”。生产实现应把 `returncode != 0` 转成明确的 `Error:` 结果。

### 8.3 并发认领仍有竞争窗口

教学版的 `claim_task()` 做了状态、owner 和依赖检查，但没有文件锁。两个队友几乎同时读取同一 pending 文件时，仍可能发生读-改-写竞争。

README 中也说明真实实现应使用文件锁，把“读取任务 -> 检查可认领性 -> 写 owner/status”放在同一个原子临界区。

## 9. 复盘

s17 的重点不是让 Lead 更聪明，而是把任务发现和任务认领下放到空闲队友。其最小闭环是：

```text
任务落盘 -> 队友 IDLE 扫描 -> 原子认领 -> 注入任务上下文 -> WORK 执行
-> complete_task -> 再次 IDLE 扫描 -> 最终 SHUTDOWN + summary
```

需要持续关注三件事：任务状态是否真实落盘、认领是否可并发安全、模型上下文是否被工具输出淹没。

