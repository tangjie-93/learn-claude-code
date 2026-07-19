# 第 2 周复盘：工程化工具

> 时间：2026-07-07 ~ 2026-07-11
> 覆盖章节：`s05_todo_write`、`s06_subagent`、`s07_skill_loading`

---

## 一、核心收获

### 1. `todo` — Agent 的外部进度条

**学到什么：**

- `todo_write` 是一个**给用户看的终端展示工具**，不是模型的内部状态管理器
- 模型看到的是自己刚写下的 todo 参数 + 代码层注入的催办提醒，而不是 `CURRENT_TODOS` 变量的完整内容
- `_current_todos` 存在 Python 内存里，主要用途是终端打印（带颜色图标）和 `rounds_since_todo` 计数器催办

**关键纠正：**

> 之前误以为 todo 是模型可随时查询的"外部工作记忆"——实际上模型调 `todo_write` 时只返回 `"Updated N tasks"`，模型是靠自己的记忆 + 催办提醒维持对进度的认知。

**三个状态：**

| 状态 | 终端图标 | 含义 |
|---|---|---|
| `pending` | `[ ]` | 还没开始 |
| `in_progress` | `[▸]` 青色 | 正在做（同时只能有一个） |
| `completed` | `[✓]` 绿色 | 已完成 |

**为什么不在聊天上下文里：**

| | 聊天上下文 | `CURRENT_TODOS` 变量 |
|---|---|---|
| token 消耗 | 每轮递增（重复打印全文） | 不变（只有催办消息注入） |
| 可靠性 | 多轮后可能遗忘或编造 | 变量不会丢 |
| 校验 | 无（模型自由发挥） | 有（`TodoManager` 验证字段） |
| 可视化 | 需要额外解析 | 直接终端打印 |

---

### 2. `subagent` — 模型驱动的任务委派

**学到什么：**

- 是**模型自己决定**什么时候用 `task` 工具，不是主 agent loop 主动调用
- 在主 agent loop 的调度层面，`task` 和 `bash`、`read`、`write` 没有任何区别——都挂在 `TOOL_HANDLERS` 字典里
- `spawn_subagent` 内部跑一套完整的 agent loop（全新 `messages`、独立的系统提示词、独立的工具列表、最多 30 轮）

**上下文隔离：**

| | 主 agent | subagent |
|---|---|---|
| 系统提示词 | 含 `task` 工具指引 | 不含 `task` 工具（防递归） |
| 对话历史 | 用户全部聊天 | 只有 `description` 一条 |
| 工具列表 | 含 `task` | 不含 `task`（防递归） |
| 返回值 | 完整对话流 | 只回传最终结果字符串 |
| hooks | 全链路生效 | 全链路生效 |

**主 agent loop 调度代码：**

```python
# s06_subagent/code_openai.py
for block in response.output:
    if block.type == "function_call":
        handler = TOOL_HANDLERS.get(block.name)   # task 和 bash 走同一个逻辑
        output = handler(**call_args(block))       # 主 loop 阻塞等待
```

---

### 3. `skill` — 按需注入的领域知识

**学到什么：**

- **发现**（启动时）：`_scan_skills()` 扫描 `skills/` 目录，解析 SKILL.md 的 frontmatter，存入 `SKILL_REGISTRY`；`build_system()` 把名称 + 描述作为轻量目录注入 SYSTEM prompt
- **加载**（运行时）：模型想用某个技能时，调 `load_skill(name)` → 从注册表取出完整 SKILL.md 内容 → 作为 `function_call_output` 注入对话

**为什么分两步（菜单 + 翻书）：**

```
SYSTEM prompt:   "Skills available: - **code-review**: ...  Use load_skill when needed."
                                       ↑ 几百 token
模型调 load_skill("code-review"):
  → 返回完整 SKILL.md 内容（可能几千 token）
                                       ↑ 只在需要时才占上下文
```

**一个可复用 skill 应该包含的 5 个部分：**

| # | 部分 | 说明 |
|---|---|---|
| ① | Frontmatter | `name` + `description`（含触发场景） |
| ② | 角色声明 | 让模型进入专业状态 |
| ③ | 工作流程 | 检查清单/步骤，别漏掉 |
| ④ | 输出格式 | 固定模板，上游可直接消费 |
| ⑤ | 边界/约束 | 禁止行为，防止越权 |

---

## 二、三大模块对比：todo vs subagent vs skill

**一句话：** 工具是手脚，todo 是便利贴，subagent 是外包工人，skill 是参考书。

| 维度 | todo | subagent | skill |
|---|---|---|---|
| **谁管理** | 代码（`CURRENT_TODOS` 变量） | 代码（`spawn_subagent` 函数） | 文件系统（`skills/` 目录） |
| **模型能看见什么** | 自己刚写的任务 + 催办提醒 | description + 最终结果字串 | 轻量目录；调 `load_skill` 后看到完整内容 |
| **在模型上下文里？** | 否 | 否（子 agent messages 跑完丢弃） | 否（只有调 `load_skill` 后才进入） |
| **对模型来说是** | 工具 `todo_write` | 工具 `task` + 隐式 agent loop | 工具 `load_skill` + 启动目录 |
| **调用频率** | 高（每轮都可能更新） | 低（复杂任务分工时） | 低（需要领域知识时） |
| **token 代价** | 极低 | 中（独立消耗，不占主 agent） | 低（目录 + 按需注入） |
| **生命周期** | 一次会话 | 被调用 → 跑完消亡 | 持久化在文件中 |

**职责边界表：**

| 模块 | 解决的问题 | 不应该承担的职责 |
|---|---|---|
| **todo** | 多步任务方向感 + 用户可视化进度 | 不替模型做决策、不执行操作 |
| **subagent** | 复杂任务分工 + 上下文隔离 | 不继承主 agent 状态、不回传过程 |
| **skill** | 跨会话可复用领域知识注入 | 不执行工具、不管理状态 |

**协作关系：**

```
skill 告诉模型"怎么做"
  → 模型规划 todo（"分几步做"）
    → 遇到复杂步骤，模型调 subagent（"这事你单独做"）
      → subagent 也可以有自己的 todo 和 skill
```

---

## 三、本周最颠覆认知的点

1. **todo 不是模型的"外部工作记忆"** —— 它主要给用户看，模型靠自己的记忆 + 注入的催办消息感知进度
2. **subagent 不是主 agent 调用的** —— 是模型像调 `bash` 一样调 `task` 工具，调度层面对所有工具一视同仁
3. **skill 不在 system prompt 里** —— 只在启动时注入一行目录，模型需要时才"翻书"，省 token
4. **不是把代码写好就行** —— todo/subagent/skill 都不是代码逻辑，而是**对模型行为的引导机制**，核心是 prompt 设计

---

## 四、和第 1 周的衔接

| 第 1 周 | 第 2 周 | 关系 |
|---|---|---|
| agent loop（能不能跑） | todo（能不能跑对路） | todo 是 agent loop 的"方向盘" |
| tools（能不能干活） | subagent（能不能分工） | subagent 把工具执行升级为委托执行 |
| hooks（能不能安全） | skill（能不能专业） | skill 把 hooks 的扩展能力应用到了知识注入领域 |
