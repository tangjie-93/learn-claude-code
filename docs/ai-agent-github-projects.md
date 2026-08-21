# AI Agent GitHub 项目学习清单

> `2026-08-20` 修订：与当前项目 `learn-claude-code`（`s01` 到 `s20` 的 `harness` 工程教程，已学至 `s18`）对照后重新梳理。
>
> 核心原则：当前项目已经深入实现过的机制，不再去外部项目重复学一遍。外部项目只看真正的增量：`RAG`、流式输出、评估、部署、`tracing`。

## 1. 两个项目的定位

先分清楚两个"当前项目"，避免混淆：

1. `learn-claude-code`：学习载体。`20` 课 `harness` 工程教程，教你从零写 `agent loop`、工具、权限、记忆、多代理等全套机制。
2. 企业 `RAG` 项目：应用目标。有前端菜单、文档导入、知识库、问答、检索、评估、日志、用户和角色模块，是学习成果最终要落地的地方。

这份清单的作用：用外部开源项目补齐 `learn-claude-code` 没教、但企业 `RAG` 项目又需要的能力。

## 2. 与当前项目的对照结论

### 2.1 已经完全覆盖，不用再去外部项目学

这些是原文档第一阶段、第二阶段的核心内容，`learn-claude-code` 里全部有实现，且是裸写底层实现（比 `LangGraph` 封装更贴近本质）：

| 能力 | 原文档想通过外部项目学 | 当前项目对应章节 |
| --- | --- | --- |
| `Agent Loop` | `langgraph-101` 入门、`agents-from-scratch` 基础 | `s01_agent_loop` |
| `Tool Calling` | `langgraph-101`、`agents-from-scratch` | `s02_tool_use`（含并发分发） |
| 权限边界、`Human-in-the-loop` | `agents-from-scratch` 的 `HITL` | `s03_permission`（审批管线）+ `s16` 计划审批 |
| `Planning` | `langgraph-101` | `s05_todo_write` |
| `Memory` | `langgraph-101`、`agents-from-scratch` | `s09_memory`（选择、提取、固化三子系统） |
| 上下文管理 | 无对应 | `s08_context_compact`（多层压缩） |
| 错误恢复 | `agents-from-scratch` | `s11_error_recovery`（重试、换路、降级） |
| 长任务持久化 | `deployment-cookbook` 的任务部分 | `s12_task_system` + `s13_background_tasks` + `s14_cron` |
| `Subagent`、多代理协作 | `OpenHands`、`autogen`、`crewAI` 的多代理部分 | `s06_subagent` + `s15_agent_teams` + `s16_team_protocols` + `s17_autonomous_agents` |
| 执行隔离 | `OpenHands` 的隔离部分 | `s18_worktree_isolation`（目录级隔离） |
| 外部能力接入 | 无对应 | `s19_mcp_plugin`（`MCP` 多 `transport`） |
| 前端展示中间步骤 | `deployment-cookbook` 的前端部分 | `web-vue/`（执行流面板、时间线、模拟器） |

结论：原文档"第一阶段：建立 `Agent` 主干"（`langgraph-101` + `agents-from-scratch`）整段可以跳过。你不仅跑通过，还自己写过实现。

### 2.2 部分覆盖，只看增量

| 项目 | 已会（跳过） | 只看增量 |
| --- | --- | --- |
| `openai/openai-agents-python` | `tools`（对应 `s02`）、`guardrails`（对应 `s03`） | `handoffs`（代理交接）、`tracing`、`sessions` |
| `OpenHands/OpenHands` | 终端工具（`s01`）、文件操作（`s02`）、多代理（`s15` 到 `s17`） | 容器沙箱（`s18` 只是目录隔离）、浏览器工具、真实产品的模块划分 |
| `langchain-ai/langgraph-101` | `Agent` 基础、工具、记忆、多代理、人工介入 | 流式输出、`LangGraph` 的 `state graph` 和 `checkpoint` 视角（了解即可） |

### 2.3 完全没覆盖，是真正的学习重点

1. `RAG Agent`：索引链路、检索链路、权限过滤、`metadata` 过滤、引用解释。当前项目完全没有，企业 `RAG` 项目的核心。
2. 流式输出与流式协议：当前项目代码均为非流式整段返回。
3. 评估：当前项目只有 `tests/` 单元测试，没有 `eval dataset` 和人工反馈闭环。
4. 生产化部署：线程历史持久化、并发、生产运行时。
5. `Observability`：`trace id`、耗时、`token`、错误类型的追踪体系。
6. 结构化输出与类型安全：`Structured Output` 的校验体系。

## 3. 项目清单（修订后）

| 序号 | 优先级 | 项目 | 学习定位 | 怎么读 |
| --- | --- | --- | --- | --- |
| 1 | `P0` | [`langchain-ai/retrieval-agent-template`](https://github.com/langchain-ai/retrieval-agent-template) | 唯一的 `RAG Agent` 主线，重点中的重点 | 完整读：索引图、检索图、用户隔离、上下文问答 |
| 2 | `P1` | [`langchain-ai/deployment-cookbook`](https://github.com/langchain-ai/deployment-cookbook) | 生产化：流式协议、线程历史、持久化、部署 | 只读运行时和持久化部分 |
| 3 | `P1` | [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) | `handoffs`、`tracing`、`sessions` 三个增量点 | 跳过 `tools` 和 `guardrails` 章节 |
| 4 | `P2` | [`pydantic/pydantic-ai`](https://github.com/pydantic/pydantic-ai) | 结构化输出、类型安全 | 读 `structured output` 文档即可 |
| 5 | `P2` | [`OpenHands/OpenHands`](https://github.com/OpenHands/OpenHands) | 真实复杂系统参考：沙箱、浏览器工具 | 只看架构文档和 `README`，不逐行读源码 |
| 6 | `P3` | [`langchain-ai/langgraph-101`](https://github.com/langchain-ai/langgraph-101) | `LangGraph` 视角对照（状态图、`checkpoint`） | 翻 `README` 对照即可，不跑环境 |

以下项目从清单中删除，理由：

1. `langchain-ai/agents-from-scratch`：当前项目本身就是一套更完整的 `agents-from-scratch`（`20` 课从零写到综合），重复。仅当需要它的 `evaluation` 章节时单独查阅。
2. `crewAIInc/crewAI`、`microsoft/autogen`：多代理编排框架。当前项目 `s15` 到 `s17` 的 `mailbox` 自组织模式已覆盖同类问题，且 `README` 的核心观点正是批判编排型 `agent`。仅作为框架选型对比时翻一下。
3. `microsoft/agenticcookbook`：泛泛的示例集，与目标无关。

## 4. 学习顺序（修订后）

原来四周的东西砍掉一半，只剩两条线：

### 4.1 第一条线：`RAG Agent`（对齐企业项目）

读 [`retrieval-agent-template`](https://github.com/langchain-ai/retrieval-agent-template)，回答这些问题：

1. 文档如何进入索引流程？导入失败怎么恢复？
2. 检索图和回答图如何拆分？
3. 用户、权限组、知识库如何影响检索范围？
4. `metadata` 怎么参与过滤？
5. 检索结果的引用如何生成和展示？

对照企业 `RAG` 项目的映射关系：

| 企业项目模块 | 可参考项目 | 可迁移设计 |
| --- | --- | --- |
| 文档导入 | `retrieval-agent-template` | `indexing graph`、导入状态机、失败恢复 |
| 知识检索 | `retrieval-agent-template` | `retrieval graph`、权限过滤、上下文组装 |
| 智能问答 | `openai-agents-python` | `handoffs`、`guardrails`（已有 `s03` 基础，补 `SDK` 视角） |
| 运行日志 | `openai-agents-python` | `tracing`、`session`、`step` 记录 |
| 效果评估 | `retrieval-agent-template` + 自建 | 评估数据集、人工反馈闭环 |

最小产出：

1. 给企业 `RAG` 项目画出一张索引链路图。
2. 给企业 `RAG` 项目画出一张问答链路图。
3. 把权限过滤逻辑写成明确规则。

### 4.2 第二条线：生产化（补齐工程短板）

读 [`deployment-cookbook`](https://github.com/langchain-ai/deployment-cookbook) 的运行时部分 + [`openai-agents-python`](https://github.com/openai/openai-agents-python) 的 `tracing`/`sessions`，重点：

1. `Agent` 状态如何持久化（对照 `s12` 的磁盘任务系统，看生产级做法）。
2. 流式响应协议如何设计。
3. 后端如何保存线程历史。
4. `trace id`、耗时、`token`、错误类型如何追踪。

最小产出：

1. 给企业项目补一份"生产化检查清单"。
2. 设计一个 `Agent Run` / `Agent Step` 表结构草稿。

## 5. 和企业 `RAG` 项目的改造建议

企业项目已有前端菜单、文档导入、知识库、问答、检索、评估、日志、用户和角色模块。按方向排序：

1. 把问答流程显式建模成 `Agent Run`（当前项目 `s12` 的任务结构可直接参考）。
2. 把每次工具调用保存成 `Agent Step`。
3. 给检索结果增加权限过滤和引用解释（`retrieval-agent-template` 主线）。
4. 给导入任务增加状态机和失败重试（`s11` + `s13` 已有模式可迁移）。
5. 给低置信度回答建立人工复核流程（`s03` 审批管线可迁移）。
6. 给日志模块增加 `trace id`、耗时、`token` 和错误类型。
7. 给前端增加 `Agent` 执行过程面板（`web-vue` 的 `ExecutionFlowPanel` 可直接参考）。
8. 给评估模块增加标准问题集和人工反馈闭环。

## 6. 修订后的学习安排

原两周计划里第一周全部与当前项目重复，压缩为一周，聚焦增量：

1. 第 `1` 天：跑通 `retrieval-agent-template`，画出索引图和检索图。
2. 第 `2` 天：研究用户隔离、权限组、`metadata` 过滤，对照企业项目权限模块写规则。
3. 第 `3` 天：研究引用生成和上下文组装，写一页"企业 `RAG` 问答链路说明"。
4. 第 `4` 天：读 `openai-agents-python` 的 `handoffs`、`tracing`、`sessions`。
5. 第 `5` 天：读 `deployment-cookbook` 的流式协议和线程历史持久化。
6. 第 `6` 天：设计 `Agent Run` / `Agent Step` 表结构 + 生产化检查清单。
7. 第 `7` 天：复盘，翻一遍 `langgraph-101` 的 `state graph` 做对照，确定企业项目下一步改造优先级。

## 7. 第一件事

今天先做一件事：跑通 [`retrieval-agent-template`](https://github.com/langchain-ai/retrieval-agent-template)，并写下这 `3` 个问题的答案：

1. 一份文档从上传到可被检索，中间经过哪些步骤？
2. 检索时用户身份如何影响可见范围？
3. 回答里的引用是怎么追溯到原文的？
