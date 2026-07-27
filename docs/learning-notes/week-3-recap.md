# 第 3 周复盘：Agent 上下文管理原则

> 时间：2026-07-14 ~ 2026-07-18
> 覆盖章节：`s13_background_tasks`、`s14_cron_scheduler`、`s15_agent_teams`、`s16_team_protocols`

---

## 一、核心主题：上下文注入

第 1 周回答"Agent 能不能跑"，第 2 周回答"Agent 怎么做对"，第 3 周回答的核心问题是：

> **当事情不在当下发生（异步完成、定时触发、其他 Agent 执行），信息如何进入 Agent 的对话上下文？**

三种注入机制：

| 章节 | 来源 | 注入格式 | 触发方式 |
|---|---|---|---|
| s13 后台任务 | daemon 线程执行耗时命令 | `<task_notification>` XML | 完成后注入当前轮 / 下一轮用户输入前补发 |
| s14 定时任务 | cron 表达式时间匹配 | `[Scheduled task] prompt` | 调度线程推入队列 → 投递线程唤醒 Agent |
| s15/s16 Agent 团队 | 队友通过 MessageBus 发消息 | `<inbox>` JSON / 协议响应 | 收件箱轮询 + Lead 主动 check_inbox |

---

## 二、Agent 上下文管理原则

### 原则 1：生产者-消费者解耦

所有异步信息源都通过**中间层**与 Agent 对话历史解耦：

```
后台任务结果 → background_results dict → collect_background_results() → messages
cron 触发     → cron_queue list           → consume_cron_queue()       → messages
队友消息      → .jsonl 文件邮箱           → BUS.read_inbox()           → messages
```

| 生产者 | 中间层 | 消费者 |
|---|---|---|
| worker 线程 | `background_results` (dict + Lock) | `collect_background_results()` |
| `cron_scheduler_loop` | `cron_queue` (list + Lock) | `consume_cron_queue()` |
| 队友 agent_loop | `.jsonl` 文件 | `BUS.read_inbox()` → `_process_inbox()` |

Agent 的 `messages` 列表是唯一的汇合点。生产者不知道消费者的存在，消费者不关心生产者何时完成。

### 原则 2：注入时机控制

| 时机 | 场景 | 示例 |
|---|---|---|
| **即时注入** | 当前 agent_loop 仍在运行，结果已就绪 | 后台任务在 LLM 回复前完成 → 直接追加到本轮 |
| **延迟注入** | agent_loop 已退出，结果后到达 | `pending_background_notifications` → 下一轮 `input()` 前补发 |
| **轮询注入** | daemon 线程持续检测 | `inbox_poller` 每秒检查 `BUS.peek("lead")` |
| **主动拉取** | LLM 决策调工具查询 | Lead 调用 `check_inbox` → `BUS.read_inbox("lead")` |

核心矛盾：**LLM 不知道外部世界发生了什么，必须通过"注入到 messages"来告知它。**

### 原则 3：不污染上下文

| 机制 | 控制策略 | 原因 |
|---|---|---|
| 后台任务输出 | `summary[:200]` 截断 | 防止 `npm install` 几千行输出撑爆消息窗口 |
| 队友消息 | `input=messages[-20:]` 截断最近 20 条 | 队友独立 agent_loop 不受 Lead 长历史拖累 |
| 队友对话历史 | 全新 `messages` 列表 | 上下文隔离，队友不继承 Lead 的完整历史 |
| cron 注入 | 合并同一分钟的任务为一条 | 防止同分钟多个 cron 任务重复注入 |

**关键洞察：上下文是稀缺资源（token 窗口有限），注入的信息必须被裁剪和优先级排序。**

### 原则 4：消费语义一致性

Agent Teams 中文件邮箱的 `read_inbox()` 是**破坏性消费**：

```python
msgs = [json.loads(line) for line in inbox.read_text().splitlines()]
inbox.unlink()  # 读后即删
```

- 每条消息只被消费一次（at-most-once）
- Lead 的 `check_inbox` 和 `inbox_poller` 两条路径共享同一消费语义
- 先到先得：谁先 `read_inbox()` 谁消费消息，另一方看到空邮箱

对于后台任务，`background_tasks.pop(bg_id)` 同样是一次性消费。

### 原则 5：线程安全边界

三个维度：

| 维度 | 实现 | 保护的资源 |
|---|---|---|
| 共享状态 | `background_lock = threading.Lock()` | `background_tasks`、`background_results` |
| 互斥执行 | `agent_lock = threading.Lock()` | 同一时间只有一个 agent_loop 运行 |
| 文件并发 | 教学版无锁；真实 CC 用 `proper-lockfile` | `.jsonl` 文件 append |

文件 append 在多线程中不是原子的（Python 中 `f.write()` 对大字符串可能分块），多 teammate 并发写同一邮箱时可能行交错。

---

## 三、事件驱动模型演进

### 第 1-2 周：用户驱动

```
用户输入 → agent_loop → 返回结果 → 等下次输入
```

### 第 3 周：多事件源驱动

```
用户输入 ──┐
           ├──→ events.get() → agent_loop → 返回
异步唤醒 ──┘
```

s15 引入的 `queue.Queue()` + `input_reader` + `inbox_poller` 三线程模型，让 Agent 从"只响应用户"升级为"响应多个事件源"：

```
input_reader (daemon)  ──→ events.put("user", line)  ──┐
inbox_poller (daemon)  ──→ events.put("wake", None)  ──┤
cron_scheduler (daemon)──→ cron_queue ──→ processor ──→ agent_lock ──→ agent_loop
```

---

## 四、三大模块对比

| 维度 | 后台任务 | 定时任务 | Agent 团队 |
|---|---|---|---|
| **解决的问题** | 耗时命令不阻塞 | 周期性自动执行 | 复杂任务并行分工 |
| **事件来源** | 工具执行完成 | 时间表达式匹配 | 队友消息到达 |
| **执行主体** | daemon 线程跑单个命令 | LLM 决定执行什么 | daemon 线程跑完整 agent_loop |
| **通信方式** | XML 注入 | prompt 注入 | 文件邮箱 + 协议 |
| **上下文影响** | 1 条通知 / 任务 | 1 条 prompt / 任务 | 完整对话流 / 队友 |
| **状态管理** | dict + Lock | dict + Lock + 持久化 | dict + 文件 + 协议状态机 |

**组合关系：**

```
定时任务触发 → Agent 进入 agent_loop
  → LLM 决定调用工具
    → 工具耗时 → 后台任务执行
    → 工具复杂 → spawn teammate（teammate 内部也可以有后台任务）
      → teammate 完成 → 结果通过 MessageBus 回传
        → inbox_poller 检测 → 注入 Lead 上下文
```

---

## 五、本周最颠覆认知的点

1. **Agent 的"外部世界"只有 `messages` 列表** —— 所有异步信息（后台结果、定时触发、队友消息）最终都变成 `messages.append(...)`，没有其他渠道
2. **上下文是稀缺资源** —— 不是在聊天窗口里塞得越多越好；截断、裁剪、合并、延迟注入都是必要的控制手段
3. **daemon 线程 + 锁 + 队列是 Agent 的"神经系统"** —— 让 Agent 从单线程阻塞模型走向多线程事件驱动模型
4. **消费语义决定了信息可靠性** —— 破坏性消费（`read + unlink`、`pop`）意味着 at-most-once，需要精心设计以避免消息丢失
5. **文件作为通信媒介是双刃剑** —— 简单但不可靠（非原子、无事务、无 ACK），真实系统需要 proper-lockfile 或消息队列

---

## 六、和第 2 周的衔接

| 第 2 周 | 第 3 周 | 关系 |
|---|---|---|
| todo（进度管理） | 后台任务（异步执行） | todo 标记"要做什么"，后台任务保证"做了不卡住" |
| subagent（任务委派） | Agent 团队（多 Agent） | subagent 是临时外包，Agent 团队是持久协作 |
| skill（知识注入） | 上下文注入（信息注入） | skill 注入"怎么做的知识"，上下文注入"发生了什么的事实" |

---

## 七、Agent 上下文管理原则（速查卡）

```
┌────────────────────────────────────────────────────┐
│             Agent 上下文管理五原则                    │
├────────────────────────────────────────────────────┤
│ 1. 生产者-消费者解耦：信息源不直接写 messages         │
│ 2. 注入时机控制：即时 / 延迟 / 轮询 / 主动拉取       │
│ 3. 不污染上下文：截断长输出、限制历史轮数             │
│ 4. 消费语义一致：破坏性消费，每条消息只处理一次       │
│ 5. 线程安全边界：锁保护共享状态，文件并发需额外处理   │
└────────────────────────────────────────────────────┘
```
