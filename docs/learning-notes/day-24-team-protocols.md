# Day 24 学习记录

## 1. 今天学习的文件

- `s16_team_protocols/code_openai.py` -- 基于 request_id 的 Lead-Teammate 结构化请求-响应协议

## 2. 核心概念

**s16 在 s15 MessageBus 基础上增加了结构化协议层：Lead 和 Teammate 之间不再是自由文本消息，而是带 request_id、状态追踪和类型匹配的请求-响应模式。ProtocolState 追踪每个协议请求的生命周期（pending → approved/rejected），match_response 通过 request_id 关联响应。**

### 2.1 从自由消息到结构化协议

```
s15:  BUS.send("lead", "bob", "do X", "message")    → 完全自由，无状态
s16:  BUS.send("lead", "bob", "do X", "shutdown_request", {"request_id": req_id})  → 结构化
```

| 维度 | s15 | s16 |
|---|---|---|
| 消息格式 | 自由文本 | type + metadata + request_id |
| 响应关联 | 无（LLM 猜） | match_response(request_id) 精确匹配 |
| 状态追踪 | 无 | ProtocolState (pending/approved/rejected) |
| Lead 工具 | spawn_teammate, send_message, check_inbox | + request_shutdown, request_plan, review_plan |
| Teammate 工具 | bash, read_file, write_file, send_message | + submit_plan |

### 2.2 三种协议流程

```
┌─────────────────────────────────────────────────────────┐
│  1. shutdown 协议                                       │
│  Lead: request_shutdown("bob")                          │
│    → BUS.send(..., "shutdown_request", {req_id})        │
│  Teammate: handle_inbox_message → shutdown_request      │
│    → BUS.send(..., "shutdown_response", {req_id, approve:true})
│    → return True (停止运行)                              │
│  Lead: consume_lead_inbox → match_response(req_id)      │
│    → ProtocolState.status = "approved"                   │
├─────────────────────────────────────────────────────────┤
│  2. plan_approval 协议                                  │
│  Lead: request_plan("bob", "task")                      │
│    → BUS.send(..., "message")  (普通消息，让队友提交计划) │
│  Teammate: LLM 决策 → 调用 submit_plan("plan text")     │
│    → _teammate_submit_plan: ProtocolState +             │
│      BUS.send("plan_approval_request", {req_id})        │
│  Lead: consume_lead_inbox → match_response(req_id)      │
│    → lead_loop 中看到 pending_requests，下轮调 review_plan│
│  Lead: review_plan(req_id, approve=True/False)          │
│    → BUS.send("plan_approval_response", {approve})      │
│  Teammate: handle_inbox_message → plan_approval_response│
│    → 注入 "[Plan approved]" 或 "[Plan rejected]" 到 messages
│    → 继续或重新规划                                      │
├─────────────────────────────────────────────────────────┤
│  3. 普通消息（s15 遗留）                                 │
│  Lead: send_message / spawn_teammate prompt             │
│  Teammate: _process_inbox → 注入 <inbox> JSON           │
│  Teammate: → 完成 → BUS.send(..., "result")             │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 关键代码分析

### 3.1 ProtocolState 状态管理

```python
@dataclass
class ProtocolState:
    request_id: str       # req_XXXXXX，关联请求和响应
    type: str             # "shutdown" | "plan_approval"
    sender: str           # 发起方
    target: str           # 接收方
    status: str           # pending → approved | rejected
    payload: str          # plan 文本或 shutdown 原因
    created_at: float = field(default_factory=time.time)  # 每个实例独立时间戳

pending_requests: dict[str, ProtocolState] = {}  # request_id → state
```

**为什么用 `field(default_factory=time.time)` 而不是 `= time.time()`？**

dataclass 默认参数在**类定义时**就求值。如果写 `= time.time()`，类加载那一瞬间的时间戳会被所有实例共享。`default_factory` 让每次创建新实例时才调用 `time.time()`。

### 3.2 match_response — 请求-响应关联

```python
def match_response(response_type: str, request_id: str, approve: bool):
    """三重校验：
    1. request_id 必须存在于 pending_requests
    2. response_type 必须与请求类型匹配（shutdown_request ↔ shutdown_response）
    3. status 必须为 pending（防重复消费）
    """
    state = pending_requests.get(request_id)
    if not state: return  # 未知 request_id
    if state.type == "shutdown" and response_type != "shutdown_response": return
    if state.type == "plan_approval" and response_type != "plan_approval_response": return
    if state.status != "pending": return  # 已处理，忽略
    state.status = "approved" if approve else "rejected"
```

**关键设计**：类型校验防止消息类型不匹配时被错误关联。

### 3.3 consume_lead_inbox — 统一收件消费

s16 的 Lead 收件箱消费有两个入口，s15 会导致重复消费或漏消费。s16 统一为一个函数：

```python
def consume_lead_inbox(route_protocol: bool = True) -> list[dict]:
    msgs = BUS.read_inbox("lead")          # 一次性消费
    if route_protocol:
        for msg in msgs:
            # 自动路由协议响应到 match_response
            if msg.get("type", "").endswith("_response"):
                match_response(msg_type, req_id, approve)
    return msgs  # 返回所有消息供调用方展示
```

| 调用方 | 用途 | route_protocol |
|---|---|---|
| `run_check_inbox()` | LLM 主动检查收件箱 | True |
| 主循环 (L1102) | 每轮结束自动注入 | True |

### 3.4 _process_inbox — 收件箱处理（公共函数）

从外层循环和 idle loop 两段重复代码中抽离：

```python
def _process_inbox(name: str, messages: list) -> tuple[bool, bool]:
    """返回 (should_shutdown, has_new_messages)"""
    inbox = BUS.read_inbox(name)
    if not inbox:
        return False, False
    non_protocol = []
    for msg in inbox:
        if msg.get("type") in ("shutdown_request", "plan_approval_response"):
            should_stop = handle_inbox_message(name, msg, messages)
            if should_stop:
                return True, False    # shutdown → 停止
        else:
            non_protocol.append(msg)
    if non_protocol:
        messages.append({"role": "user", "content": "<inbox>" + json.dumps(non_protocol) + "</inbox>"})
        return False, True            # 有新消息 → LLM 继续
    return False, False               # 空，无事发生
```

### 3.5 Teammate 的主工作循环

```
while not shutdown_requested:                    # 外层循环
    should_stop, _ = _process_inbox(...)         # 步骤1：收件
    if should_stop: break                         # shutdown → 退出
    response = LLM(messages[-20:])                # 步骤2：推理
    if not function_calls(response):              # 步骤3：无工具调用 → idle loop
        while not shutdown_requested:
            sleep(1)
            should_stop, has_new = _process_inbox(...)  # 轮询收件
            if should_stop: break                        # shutdown
            if has_new: break                            # 新消息 → 回外层
    results = execute_tools(response)             # 步骤4：执行工具
```

**两层 `while not shutdown_requested`**：外层是工作循环，内层是 idle 等待。队友完成任务后不退出，进入 polling 等待新指令或 shutdown 信号。

### 3.6 _teammate_submit_plan — 协议 vs 代码的边界

```python
def _teammate_submit_plan(from_name: str, plan: str) -> str:
    """注意：这是协议层请求，不是代码级关卡。
    队友线程在 submit_plan 后继续运行——它仍可调用 bash/write 等工具。
    真正的执行约束依赖于模型在收到审批响应前等待。
    代码级关卡需要阻塞队友的工具分发，直到审批到达。"""
    req_id = new_request_id()
    pending_requests[req_id] = ProtocolState(...)
    BUS.send(from_name, "lead", plan, "plan_approval_request", {"request_id": req_id})
    return f"Plan submitted ({req_id}). Waiting for approval..."
```

**关键洞察**：协议是"社交约定"（prompt 层面，靠模型自觉），不是"物理强制"（代码层面拦截）。真正的审批关卡需要代码在工具分发前检查 `pending_approval` 标记。

---

## 4. 架构图

### 4.1 消息流向

```
                     Lead 主循环
                    ┌───────────────────┐
                    │ consume_lead_inbox│ ← 每轮结束后自动消费
                    │   match_response  │
                    └──────┬────────────┘
                           │ BUS.read_inbox("lead")
                    ┌──────┴──────────────────┐
                    │    .jsonl 文件邮箱       │
                    └──────┬──────────────────┘
                           │
        ┌──────────────────┼──────────────────────┐
        │                  │                      │
  shutdown_response  plan_approval_request   plan_approval_response
  (teammate → lead)  (teammate → lead)       (lead → teammate)
        │                  │                      │
        ▼                  ▼                      ▼
  match_response     match_response          handle_inbox_message
  status=approved    status=pending          注入 LLM messages

  发送方:
  Teammate shutdown      Teammate submit_plan    Lead review_plan
```

### 4.2 协议生命周期

```
shutdown 协议:
  pending_requests[req_id]                          match_response(approve=True)
  ────────[pending]────────────────────────────────────[approved]
  ▲                                                     ▲
  request_shutdown                                     consume_lead_inbox

plan_approval 协议:
  pending_requests[req_id]             review_plan(approve=True)
  ────────[pending]─────────────────────────[approved/rejected]
  ▲                              ▲
  _teammate_submit_plan         LLM 看到后决策调 review_plan
```

---

## 5. 关键设计决策

### 5.1 为什么 shutdown 和 plan_approval 是不同的协议类型？

| | shutdown | plan_approval |
|---|---|---|
| 方向 | Lead → Teammate → Lead | Teammate → Lead → Teammate |
| 轮次 | 1 轮（请求+响应） | 2 轮（请求+审批） |
| 状态变更 | 队友 stop loop | 队友收到 approve/reject 后调整行为 |
| Lead 感知 | consume_lead_inbox → match_response | pending_requests 中有记录 → LLM 下一轮看到 → 调 review_plan |

### 5.2 为什么 Lead 需要手动调 review_plan？

plan_approval 的响应不是自动的。审阅计划需要人类/LLM 判断——may需要细读计划内容、评估可行性。自动 approve 只能用于测试环境。

### 5.3 协议消息 vs 普通消息的处理差异

```python
# 协议消息：优先级最高，先路由
if msg.get("type") in ("shutdown_request", "plan_approval_response"):
    should_stop = handle_inbox_message(name, msg, messages)

# 普通消息：注入 messages 供 LLM 读取
else:
    non_protocol.append(msg)
    # → <inbox> JSON → LLM 自行理解
```

---

## 6. 扩展分析

### 6.1 协议消息丢失

如果 Lead 在 `consume_lead_inbox` 和 `review_plan` 之间 crash，`plan_approval_request` 已被消费（read+unlink），但 `pending_requests` 状态仍为 pending。重启后 plan 丢失——因为 `.jsonl` 文件已被删除。

**方案**：先消费再持久化 pending_requests 到硬盘，或改为 at-least-once 语义（消费前备份）。

### 6.2 多协议并发

`pending_requests` 是全局 dict，一个 Lead 可以同时有多个协议请求 pending（例如同时等多个 teammate 的 plan）。但 `consume_lead_inbox` 一次性消费所有消息，顺序处理——如果先消费 shutdown_response 再消费 plan_approval_request，而 LLM 还没看到 plan，就会丢失。

### 6.3 非原子文件操作

`read_inbox` 的 `read_text + unlink` 是非原子的。如果两个线程同时读同一个 `.jsonl`，可能一个读到空（另一个已 unlink），导致消息丢失。

---

## 7. 与 s15 的对比

| 改动 | s15 | s16 |
|---|---|---|
| 协议结构 | 无，纯文本消息 | ProtocolState + request_id + type dispatch |
| 收件箱消费 | 两处独立调用，可能重复/漏消费 | 统一 consume_lead_inbox |
| 收件箱处理 | 两段重复代码 | _process_inbox 公共函数 |
| 队友退出 | 10 轮固定退出 | shutdown 协议 + idle loop |
| 队友工具 | 4 个 | + submit_plan |
| Lead 工具 | 3 个（spawn, send, check） | + 3 个协议工具 |
| 固定流程 | 自由发送任何消息 | shutdown/plan_approval 两种结构化流程 |

---

## 8. 存疑问题

- _process_inbox 的 `BUS.read_inbox` 破坏了消费语义——如果协议消息和非协议消息混在同一个 inbox 里，处理顺序是遍历决定，但 `read_inbox` 一次性全部拿走并删除。
- 队友 submit_plan 后虽然返回 "Waiting for approval..."，但 LLM 没有义务等价。如果模型在下一轮直接执行工具，计划审批就形同虚设。
- match_response 在 `consume_lead_inbox` 中被调用，但如果协议响应到达时 Lead 正处于 agent_loop 的 LLM 调用中，要等到下一轮 `consume_lead_inbox` 才被处理——异步延迟一整个 agent_loop 轮次。

---

## 9. 明天验证点

- s17 是否会增加更多协议类型（如 ask_user、escalate）
- 真实 CC 中是否用 `proper-lockfile` 解决了 .jsonl 并发安全问题
- 协议状态机是否会从 pending → 中间状态（如 reviewing）而不是 binary approve/reject
