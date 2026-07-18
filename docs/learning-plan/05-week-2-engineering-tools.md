# 第 2 周：让 agent 更像工程工具

本周目标：理解 agent 如何管理任务、拆分职责、按需加载领域知识。

## Day 8：`todo` 管理

### 学习材料

- `s05_todo_write/code.py`

### 具体任务

1. 阅读 `TodoManager`。
2. 理解 `todo` 的状态字段。

   只允许三种状态：
   - pending     — 还没开始
   - in\_progress — 正在做（同时只能有一个）
   - completed   — 已完成
3. 思考 `todo` 为什么不是普通聊天上下文。

   **todo 是模型的便利贴，但模型写了就扔了，只有用户能看见墙上贴了哪些便利贴。**

   把 todo 存到 Python 变量 `_current_todos` 里，而不是放在 `messages` 对话历史里：

   | | 放在聊天上下文（messages） | 放在外部变量（`_current_todos`） |
   |---|---|---|
   | todo 谁规划的 | 模型 | 模型（一样） |
   | 存在哪 | messages 消息里 | Python 内存里 |
   | 每轮 token 消耗 | 越来越大（每轮要重发整个列表） | 不变（不占 token） |
   | 会不会忘 | 可能（上下文超长时丢失） | 不会（变量不会忘） |

   实际上 `run_todo_write` 返回给模型的值只有 `"Updated N tasks"`（[tools.py#L126](https://github.com/tangjie-93/learn-claude-code/blob/main/common/tools.py#L126)），模型**能看到的始终只有自己刚写的计划**。模型靠三项东西维持对 todo 的认知：
   - 自己的记忆（聊天历史里写过什么）
   - 系统提示词：`"Before starting any multi-step task, use todo_write to plan your steps"`
   - 催办提醒：连续 3 轮没更新时注入 `"<reminder>Update your todos.</reminder>"`

   `_current_todos` 的额外价值：终端彩色打印给用户看进度、催办计数追踪。模型自己不需要读到完整列表。

### 产出

解释为什么 agent 需要显式 `todo` 状态。

Agent 需要显式 `todo` 状态，**核心不是为了给模型自己看，而是给用户和外部系统看**。

**从 3 个角色的视角：**

| 角色 | 没有 todo | 有 todo |
|---|---|---|
| **用户** | 只能等模型输出，不知道它"计划做什么、做到哪了" | 终端实时展示任务清单，一眼看到进度 |
| **模型** | 凭记忆"记得"要做什么，多轮后会遗忘、跑偏 | 被催办提醒拉回正轨，不至于无限偏离 |
| **外部系统** | 无法知道模型状态 | `rounds_since_todo` 计数器可触发干预 |

**为什么不能靠聊天上下文：**

聊天上下文是模型的"短期记忆"，越长越模糊、越贵。todo 存外部变量里，既省 token，又让用户和监督系统介入。

**一个具体场景：**

模型做"读代码 → 分析 → 写文档"时，如果中途卡在分析某行代码又去调 bash 查别的。没有 todo 的话：
- 用户只会看到一堆 bash 输出，不知道模型到底在干嘛
- 模型可能迷失在细节里忘记初始任务

有 `_current_todos` 后：
- 用户终端看到 `[▸] 分析代码` 卡着不动
- `rounds_since_todo >= 3` → 注入 `"<reminder>Update your todos.</reminder>"`
- 模型被拉回来继续，不会无限跑偏

## Day 9：`todo` 测试

### 学习材料

- `tests/test_todo_write_string_input.py`

### 具体任务

1. 阅读测试输入。
2. 找到测试期待的输出。
3. 理解字符串输入和结构化输入的差异。

### 产出

总结测试覆盖了哪些边界。

## Day 10：`subagent`

### 学习材料

- `s06_subagent/code.py`

### 具体任务

1. 找到 `run_subagent`。
   - OpenAI 版：[code_openai.py#L222](https://github.com/tangjie-93/learn-claude-code/blob/main/s06_subagent/code_openai.py#L222) `spawn_subagent(description: str) -> str`
2. 理解主 agent 如何调用 `subagent`。

   **不是主 agent 主动调用，而是模型自行决定什么时候用 `task` 工具——调度层面和 `bash` 没有任何区别。**

   主 agent loop 的代码对所有工具一视同仁，不分「普通工具」和「子代理」：

   ```python
   # 主 agent loop 里的工具调度（code_openai.py#L280-L283）
   handler = TOOL_HANDLERS.get(block.name)   # 模型说调 task → 找到 spawn_subagent
   output = handler(**call_args(block))       # 同步执行，主 loop 阻塞等待
   ```

   唯一区别在 `spawn_subagent` 内部——它自己跑了一套 agent loop：

   ```
   主 agent loop（对 task 无特殊处理）        spawn_subagent 内部
   ────────────────────────────────        ──────────────────
   while True:                             messages = [{"role":"user", "content": description}]
       response = LLM(...)                 for _ in range(30):   ← 安全限制
       for block in function_calls:            response = LLM(SUB_SYSTEM, SUB_TOOLS, ...)
           handler = TOOL_HANDLERS[name]        if 无工具调用: break
           output = handler(**args)  ←─调用──→  执行工具 → 回填结果
           # 如果是 task，这里要等很久        return 最终总结文本  ←─返回──→ output 拿到结果字串
   ```

   **一句话：** 主 agent loop 眼里 `task` 只是个名字，跟 `bash`/`read`/`write` 并列在 `TOOL_HANDLERS` 字典里。模型觉得需要分工就用，不需要就不用。

   **注册方式：** 和其他工具完全一样
   ```python
   TOOLS.append({"type": "function", "name": "task", "description": "..."})
   TOOL_HANDLERS["task"] = spawn_subagent
   ```

3. 判断 `subagent` 是否共享主上下文。
   - **不共享。** `spawn_subagent` 内部创建了全新的 `messages = [{"role": "user", "content": description}]`，不继承主 agent 的任何聊天历史。

### 产出

说明 `subagent` 与主 agent 的上下文隔离方式。

**上下文隔离 = 全新的 messages 列表 + 独立的系统提示词 + 无 task 工具防递归**

```python
# code_openai.py#L225
messages = [{"role": "user", "content": description}]  # ← 只有这一条，不继承主 agent 的任何历史
```

子 agent 跑完后，整个 `messages` 被丢弃（[L285](https://github.com/tangjie-93/learn-claude-code/blob/main/s06_subagent/code_openai.py#L285)），只返回一个总结字符串给主 agent。主 agent 像调 `bash` 一样拿到结果，不需要知道子 agent 内部发生了什么。

**隔离带来的好处：**
- **上下文不膨胀**：子 agent 的分析过程不占主 agent 的 token
- **职责清晰**：子 agent 有自己专用的系统提示词，不会和主逻辑混在一起
- **防递归**：子 agent 的工具列表里没 `task`，不能无限套娃

## Day 11：`subagent` 练习

### 具体任务

设计一个 `code-review subagent prompt`。

需要包含：

- 角色
- 输入
- 输出格式
- 不允许做什么
- 何时返回阻塞问题

---

<details>
<summary>参考：项目中已有的 code-review Skill（skills/code-review/SKILL.md）</summary>

项目已内置一份完整的 code-review skill，作为 subagent 的 prompt 参考。最终 subagent 的 system prompt 会基于它生成。
</details>

---

**设计分析：**

#### 1. 角色

```
You are a senior code reviewer. Your job is to find bugs, security vulnerabilities,
performance issues, and maintainability problems. You do NOT write or fix code —
you only report issues.
```

关键约束：**只做审查，不写代码。** 这能防止 subagent 审着审着自己改起来了。

#### 2. 输入

subagent 用 `read` 工具读取目标文件，用 `bash` 工具执行 `git diff`、`grep` 等辅助分析。输入不是"一段代码"，而是**工作区内的文件路径 + 上下文**：

- 目标文件（`read` 工具）
- git diff / log（`bash` 工具，了解改动范围）
- 相关文件或依赖（跨文件分析，`grep` 引用）

#### 3. 输出格式

输出必须**结构化**，主 agent 才能直接使用：

```markdown
## Code Review: [文件/组件名]

### Summary
[1-2 句概述]

### Critical Issues（阻塞合并的问题）
1. **[问题]** (行 N): 描述
   - Impact: 后果
   - Fix: 建议修复方案

### Improvements（建议但不阻塞）
1. **[建议]** (行 N): 描述

### Positive Notes（做得好的地方）
- [值得一提的点]

### Verdict
[ ] Ready to merge
[ ] Needs minor changes
[ ] Needs major revision
```

#### 4. 不允许做什么

为 subagent 设置行为边界，防止它越权：

| 禁止行为 | 原因 |
|---|---|
| 修改代码（`write` / `edit` 工具）| 审查者是 reporter，不是 implementer |
| 运行被审查的项目 | 避免执行未审核的代码（可能有恶意或 bug） |
| 对非代码文件做审查 | 二进制文件、图片等无法评审 |
| 评论作者本人 | 只评论代码，不人身攻击 |

实际做法：subagent 的工具列表里**不挂 `write` 和 `edit`**，从物理层面杜绝修改行为。

#### 5. 何时返回阻塞问题

阻塞问题的定义：**合并后会导致生产故障或安全事故。** 细分三类：

| 阻塞类型 | 举例 | 为什么必须拦 |
|---|---|---|
| 安全漏洞 | SQL 注入、硬编码密钥、命令注入 | 上线即风险 |
| 逻辑错误 | 空指针、类型错误、"大 bug" | 功能不可用 |
| 数据风险 | 删表而不备份、错误的事务边界 | 数据不可逆 |

非阻塞问题（improvements）：命名不规范、可以优化但当前不影响的性能、缺少注释等。

---

### 产出

写出完整 `subagent` `prompt` 草稿。

> 实际项目中，这份 prompt 来自 `skills/code-review/SKILL.md`。下面的是基于课程理解的精简版草稿。

```text
You are a senior code reviewer. Your ONLY role is to analyze code and report
findings. You NEVER modify code — your tools are read-only.

## Review Checklist

### 1. Security (always check first)
- SQL/command/XSS injection
- Hardcoded credentials or secrets
- Missing authorization checks
- Unsafe deserialization or eval()

### 2. Correctness
- Logic errors and edge cases (null, empty, boundary)
- Error handling gaps (swallowed exceptions)
- Race conditions, resource leaks

### 3. Performance
- N+1 queries, O(n^2) in hot paths
- Blocking I/O in async code
- Missing caching on repeated expensive ops

## Input
You will be given a file path or code snippet to review. Use the bash tool
for git diff/log and grep for cross-references.

## Output Format

## Code Review: [filename]

### Summary
[1-2 sentence overview]

### Critical Issues (MUST be fixed before merge)
1. **[Issue]** (line N): Description
   - Impact: What breaks
   - Fix: Suggested fix

### Improvements (optional, won't block merge)
1. **[Suggestion]** (line N): Description

### Verdict
[ ] Ready / [ ] Minor changes / [ ] Major revision

## Violations (what you must NOT do)
1. Do NOT edit or write any file — you have no write permissions
2. Do NOT execute the reviewed code
3. Do NOT review binary or non-code files

## When to report a BLOCKING issue
Return a blocking issue if the problem would cause:
- Production failure (crash, data loss, security breach)
- Unrecoverable data corruption
- User-facing broken functionality with no workaround

If the issue is purely stylistic or can be improved later, report it as
"Improvement" — NOT as blocking.
```

## Day 12：`skill` loading

### 学习材料

- `s07_skill_loading/code.py`

### 具体任务

1. 阅读 `SkillLoader`。
   - **没有单独的 SkillLoader 类。** 代码用两个模块级函数 + 一个注册表完成所有工作：
     - `_scan_skills()` — 扫描 `skills/` 目录，解析 SKILL.md → 存入 `SKILL_REGISTRY`
     - `build_system()` — 把技能目录拼入 SYSTEM prompt
     - `load_skill(name)` — 按名称从注册表取完整内容
     - `list_skills()` — 返回所有技能名称 + 一行描述（给 SYSTEM prompt 用）

2. 找到 `skill` 发现逻辑。
   - 代码：[code_openai.py#L139-L168](https://github.com/tangjie-93/learn-claude-code/blob/main/s07_skill_loading/code_openai.py#L139-L168)

   ```python
   SKILL_REGISTRY: dict[str, dict] = {}   # name → {name, description, content}

   def _scan_skills():
       """扫描 skills/ 目录，将技能名称、描述、内容加载到 SKILL_REGISTRY 中。"""
       for d in sorted(SKILLS_DIR.iterdir()):         # 遍历 skills/ 下的每个子目录
           manifest = d / "SKILL.md"                   # 找 SKILL.md
           raw = manifest.read_text()
           meta, body = _parse_frontmatter(raw)        # 解析 YAML frontmatter + Markdown body
           name = meta.get("name", d.name)             # 取 name（缺省用目录名）
           desc = meta.get("description") or ...       # 取 description
           SKILL_REGISTRY[name] = {                    # 存入注册表
               "name": name,
               "description": desc,                    # 一行简介 → 放入目录
               "content": body,                        # 完整内容 → 按需取出
           }

   _scan_skills()   # 模块 import 时自动执行
   ```

3. 理解 `skill` 如何进入 `system prompt` 或上下文。

   **两步走：发现 + 加载**

   #### 第一步：发现 — SYSTEM prompt 中注入轻量目录

   [code_openai.py#L172-L182](https://github.com/tangjie-93/learn-claude-code/blob/main/s07_skill_loading/code_openai.py#L172-L182)

   ```python
   def build_system() -> str:
       catalog = list_skills()  # → "- **code-review**: Perform code reviews..."
       return (
           f"You are a coding agent at {WORKDIR}. "
           f"Skills available:\n{catalog}\n"            # ← 告诉模型有哪些 skill（仅名称+描述，省 token）
           "Use load_skill to get full details when needed."  # ← 告诉模型怎么获取详情
       )

   SYSTEM = build_system()  # 启动时构建，之后每次 API 调用都用它
   ```

   模型看到的是：

   ```
   Skills available:
   - **code-review**: Perform thorough code reviews with security...
   - **agent-builder**: Build agent configurations...
   Use load_skill to get full details when needed.
   ```

   这一步的核心设计思想：**目录是菜单**——只放名称和一行描述到 system prompt 里，省 token。

   #### 第二步：加载 — 模型按需调用 `load_skill` 工具

   [code_openai.py#L328-L333](https://github.com/tangjie-93/learn-claude-code/blob/main/s07_skill_loading/code_openai.py#L328-L333)

   当模型觉得需要某个技能的详细信息时，像调 `bash` 一样调 `load_skill("code-review")`：

   ```python
   def load_skill(name: str) -> str:
       skill = SKILL_REGISTRY.get(name)   # 从内存注册表取，不走文件系统（安全）
       return skill["content"]            # 返回完整 SKILL.md 内容（review checklist、输出格式等）
   ```

   `load_skill` 跟 `bash`/`read`/`write` 并列注册在 `TOOL_HANDLERS`，调度方式完全一样：

   ```python
   TOOL_HANDLERS = {
       "bash": run_bash,
       "load_skill": load_skill,   # ← 和其他工具并列，无特殊处理
       ...
   }
   ```

   #### 完整数据流

   ```
   启动时:
   skills/
     code-review/SKILL.md  ──_scan_skills()──→  SKILL_REGISTRY = {
     agent-builder/SKILL.md                        "code-review":   {name, description, content},
                                                   "agent-builder": {name, description, content},
     mcp-builder/SKILL.md                          ...
                                                 }
                                                 │
   build_system() ──→ SYSTEM = "Skills available:\n  - **code-review**: ...\n  Use load_skill..."

   运行时:
   用户: "帮我 review 这段代码"
     → model 看到 SYSTEM 里有 "Skills available: - **code-review**: Perform code reviews..."
     → model 决定: 我需要这个技能 → 调 load_skill("code-review")
     → load_skill("code-review") 从 SKILL_REGISTRY 取出 content，作为 tool_result 返回
     → model 把完整 skill 内容（review checklist、输出格式等）当上下文，开始工作
   ```

### 产出

解释 SkillLoader 如何发现和加载技能。

**发现：** 启动时 `_scan_skills()` 扫描 `skills/` 下每个子目录的 `SKILL.md`，解析 frontmatter 取出 `name` 和 `description`，存入内存注册表 `SKILL_REGISTRY`。`build_system()` 把注册表中所有技能的 `name + description` 拼成轻量目录，注入 SYSTEM prompt。

**加载：** 模型在对话中看到目录后，觉得需要某个技能的详细信息时，调用 `load_skill(name)` 工具。该工具从 `SKILL_REGISTRY` 按名称查找，返回完整 SKILL.md 内容（不再访问文件系统）。内容作为 `function_call_output` 进入对话历史，模型把它当参考指南使用。

**为什么分两步而不是直接把全部内容塞进 system prompt？** 
- 省 token：4 个 skill 的完整内容可能几万 token，目录只有几百 token
- 按需：模型只在遇到相关任务时才"翻开参考书"，不浪费上下文窗口
- 类比：菜单 vs 完整菜谱——看一眼菜单就知道有什么，决定吃哪个再看做法

## Day 13：`skill` 文件结构

### 学习材料

- `skills/agent-builder/SKILL.md`
- `skills/code-review/SKILL.md`

### 具体任务

1. 阅读两个 `skill` 文件。

   **code-review**（[skills/code-review/SKILL.md](https://github.com/tangjie-93/learn-claude-code/blob/main/skills/code-review/SKILL.md)）：
   - 审查类 skill——教模型"怎么检查代码"
   - 结构：安全检查清单 → 正确性清单 → 性能清单 → 可维护性清单 → 测试清单 → 输出格式模板 → 常见反模式代码

   **agent-builder**（[skills/agent-builder/SKILL.md](https://github.com/tangjie-93/learn-claude-code/blob/main/skills/agent-builder/SKILL.md)）：
   - 设计类 skill——教模型"怎么设计 agent"
   - 结构：核心理念 → 三要素（能力/知识/上下文）→ 设计思路 → 渐进复杂度表格 → 领域示例

2. 对比它们的结构。

   两个 skill 的 frontmatter 结构完全相同，但 body 内容类型不同：

   | 维度 | code-review | agent-builder |
   |---|---|---|
   | **类型** | 执行规范（告诉模型怎么做）| 设计指南（告诉模型怎么想）|
   | **主体结构** | 检查清单 + 输出格式 | 理念 + 原则 + 参考表格 |
   | **有代码示例？** | 是（Python/JS 反模式对比）| 否（概念性内容）|
   | **有输出模板？** | 是（Critical Issues / Verdict）| 否 |
   | **触发关键词** | review、check for bugs、audit | create an agent、build an assistant |

   **共性：** 两者都有 frontmatter（name + description）、一个概览段落、以及结构化的指导（清单/表格），且都指导模型**何时输出什么**。

3. 总结一个可复用 `skill` 应该包含哪些信息。

   一个合格的 skill 最少需要 **5 个部分**：

   | # | 部分 | 内容 | 为什么需要 |
   |---|---|---|---|
   | ① | **Frontmatter** | `name` + `description`（含触发场景和关键词）| `_scan_skills()` 解析它来构建目录，`description` 决定模型会不会"点这个菜" |
   | ② | **角色声明** | `"You now have expertise in X. Follow this approach..."` | 让模型进入正确的"专业状态"，不是通用聊天 |
   | ③ | **工作流程** | 做事步骤/检查清单（如 review checklist）| 告诉模型"按什么顺序检查什么，别漏掉" |
   | ④ | **输出格式** | Markdown 模板 / 结构化要求 | 保证 subagent 返回的结果能被主 agent 直接使用，不需要二次格式转换 |
   | ⑤ | **边界/约束** | 如果有的禁止行为或特别注意事项 | 防止 skill 越权（如 code-review 里"不要改代码"） |

   **可选但推荐的额外部分：**

   - **代码示例/反模式**（code-review）：典型错误 vs 正确写法
   - **参考命令**（code-review）：`grep` 模式、`npm audit` 等辅助检查命令
   - **经验表格**（agent-builder）："什么时候加什么"，帮模型做决策
   - **领域举例**（agent-builder）：给人看的应用案例

### 产出

写出 "好 `skill` 的 5 个标准"。

1. **清晰的触发条件** — `description` 里写明"什么时候用"，含关键词和场景，确保模型能在正确时机调用
2. **结构化的指导** — 用检查清单/表格而非大段散文，模型按列表逐项执行比读长文靠谱
3. **固定的输出格式** — 提供 Markdown 模板，让 skill 的输出可被上游直接消费，不要自由发挥
4. **明确的边界** — 写明"不要做什么"（不要改代码、不要执行未审核的程序），物理层还可通过工具列表限制
5. **自包含** — 不接受外部参数、不依赖其他 skill、不假设模型已经知道上下文，skill 内部要自给自足

## Day 14：第 2 周复盘

### 具体任务

对比 `todo`、`subagent`、`skill`。

---

**一句话类比：工具是手脚，todo 是便利贴，subagent 是外包工人，skill 是参考书。**

**详细对比：**

| 维度 | todo | subagent | skill |
|---|---|---|---|
| **谁管理** | 代码（`CURRENT_TODOS` 变量）| 代码（`spawn_subagent` 函数）| 文件系统（`skills/` 目录）|
| **模型能看见什么** | 自己刚写的任务 + 催办提醒 | description + 最终结果字串 | 轻量目录（name+desc）；调 `load_skill` 后看到完整内容 |
| **存不存在模型上下文里** | 否——存在 Python 内存，偶尔被催办注入一条消息 | 否——子 agent 的 messages 跑完就丢弃 | 否——完整内容只有在模型调 `load_skill` 后才进入上下文 |
| **对模型来说是** | 一个工具 `todo_write` | 一个工具 `task` + 背后的隐式 agent loop | 一个工具 `load_skill` + 启动时注入的目录 |
| **模型主动调用次数** | 多——每轮都可能更新进度 | 少——只在"这事太复杂需要分工"时 | 少——只在"这个领域我不熟需要翻书"时 |
| **token 代价** | 极低（只注入一条催办）| 中（子 agent 独立消耗，但不占主 agent）| 低（目录占几行 + 按需注入完整内容）|
| **生命周期** | 一次会话 | 被 task 调用 → 跑完消亡 | 持久化在 SKILL.md 文件中 |

---

### 产出

写一张职责边界表：

| 模块 | 解决的问题 | 不应该承担的职责 |
|---|---|---|
| **todo** | 多步任务时帮模型保持方向感：已做什么、正在做什么、还剩什么；同时给用户可视化进度 | 不替模型做决策、不执行操作、不替代工具调用——它只是"记在哪" |
| **subagent** | 复杂任务需要分工时提供职责隔离：独立上下文、不污染主 agent、可并行 | 不继承主 agent 的任何状态、不回传中间过程、不应承担主 agent 的编排逻辑 |
| **skill** | 跨会话可复用的领域知识注入：让模型在具体场景下自动"翻开参考书"获得专业指导 | 不执行工具、不管理状态、不是代码—它只是被注入的 prompt 文本 |

**它们三者的协作关系：**

```
skill 告诉模型"怎么做"
  → 模型规划 todo（"分几步做"）
    → 遇到复杂步骤，模型调 subagent（"这事你单独做"）
      → subagent 也可以有自己的 todo 和 skill
```

