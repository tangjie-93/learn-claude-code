# 第 3 周：上下文、记忆和系统提示词

本周目标：理解长期运行 agent 的核心难点：上下文膨胀、记忆选择和策略注入。

## Day 15：`context compact`

### 学习材料

- `s08_context_compact/code.py`

### 具体任务

1. 阅读 `token` 估算逻辑。
2. 区分 `micro compact` 和 `auto compact`。
3. 找到 `compact` 前后 `messages` 的变化。

### 产出

解释 `micro compact` 和 `auto compact` 的区别。

## Day 16：compaction 测试

### 学习材料

- `tests/test_compaction_tool_pairs.py`

### 具体任务

1. 阅读测试场景。
2. 找出 `tool_use/tool_result` 成对保留的断言。
3. 思考如果配对断裂，会导致什么问题。

### 产出

说明为什么 `tool_use/tool_result` 必须成对保留。

## Day 17：`memory`

### 学习材料

- `s09_memory/code.py`
- `s09_memory/README.md`

### 具体任务

1. 区分短期上下文和长期记忆。
   - 短期上下文：当前对话中的 `messages` 列表，受 L1-L4 压缩管线管理，会话结束后丢弃。
   - 长期记忆：`.memory/` 下持久化的文件（YAML frontmatter + Markdown），跨会话存在，按相关性筛选注入当前对话。
2. 找到 `memory` 的读写位置。
   - `.memory/`，读写分两层：
     - 索引层：`MEMORY.md`（每行一条记忆），始终注入 SYSTEM prompt。
     - 详情层：单个 `.md` 文件，按需通过 `read_memory_file()` 加载全文。
3. 思考 `memory` 应该保存事实、偏好还是过程。
   - 保存事实（`project`）、偏好（`user`）、纠偏指导（`feedback`）和外部引用（`reference`），不保存过程/中间状态。

### 产出

写出短期记忆、长期记忆以及项目记忆的区别。

- 短期记忆：当前对话中的 `messages` 列表，受 L1-L4 压缩管线管理，会话结束后丢弃。
- 长期记忆：`.memory/` 下持久化的文件（`YAML frontmatter + Markdown`），跨会话存在，按相关性筛选注入。分 4 种类型：
  - `user`：用户偏好（如"喜欢用 tab 缩进"）
  - `project`：项目事实（如"技术栈 Python 3.12、入口 main.py"）
  - `feedback`：纠偏指导（如"不要用 pandas，用 polars"）
  - `reference`：外部引用（如"API 文档地址"）
- 项目记忆不是独立维度，而是长期记忆中 `type: project` 的子类，专门保存项目级事实。

## Day 18：`system prompt`

### 学习材料

- `s10_system_prompt/code.py`

### 具体任务

1. 找到 `system prompt` 构造逻辑。
2. 区分固定策略和动态上下文。
3. 思考哪些规则应该写进 prompt，哪些应该写进代码。

### 产出

总结 `system prompt` 中承载了哪些策略。

## Day 19：代码演进对比

### 学习材料

- `s01_agent_loop/code.py` 到 `s10_system_prompt/code.py`

### 具体任务

1. 每章只看新增部分。
2. 记录新增类、函数、工具。
3. 观察哪些能力是叠加式演进。

### 产出

写出 `s01` 到 `s10` 的能力演进表。

## Day 20：文档补充

### 学习材料

- `docs/zh/s01-the-agent-loop.md`
- `docs/zh/s02-tool-use.md`
- 持续阅读到 `docs/zh/s10-team-protocols.md` 中对应主题

### 具体任务

1. 补齐只看代码时遗漏的设计动机。
2. 标记和代码实现不完全一致的地方。

### 产出

补充每章设计动机。

## Day 21：第 3 周复盘

### 具体任务

整理上下文管理主题。

### 产出

写一份 “agent 上下文管理原则”。
