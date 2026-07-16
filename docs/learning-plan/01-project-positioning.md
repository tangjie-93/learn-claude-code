# 项目定位

这个仓库是一个 `Claude Code` / `Coding Agent Harness` 教程项目。它的核心不是简单演示如何调用大模型 `API`，而是通过逐章递进的方式，展示一个 `coding agent` 的运行外壳如何从最小循环逐步成长为完整系统。

可以把它理解为三部分：

| 模块 | 路径 | 作用 |
| --- | --- | --- |
| `Python` agent 示例 | `s01_agent_loop` 到 `s20_comprehensive`、`agents/` | 展示 `agent loop`、工具调用、权限、任务系统、`subagent`、`skills`、`memory`、`MCP` 等核心能力 |
| 课程文档 | `README*.md`、`docs/{en,zh,ja}`、各章节 `README.md` | 解释每章的设计动机、概念和架构 |
| 可视化课程网站 | `web/` | 用 `Next.js` 展示章节、代码、流程图、模拟器、`diff` 和可视化组件 |

项目的主线是：

```text
最小 agent loop
  -> 工具系统
  -> 权限与 hooks
  -> todo / subagent / skill
  -> context compact / memory
  -> task system / background tasks
  -> agent teams / protocols
  -> worktree isolation / MCP plugin / comprehensive harness
```

学习这个项目的重点不是背 `API`，而是理解一个真实 `agent harness` 的工程结构：

- 模型如何观察环境
- 工具如何暴露给模型
- 工具结果如何回流到上下文
- 权限、安全边界和审批如何设计
- 任务状态如何持久化
- `subagent`、`skill`、`memory` 如何扩展 agent 能力
- 多 agent 协作和长期任务如何组织

## 学习重点

这个项目真正值得投入时间的地方，是它把 `agent harness` 拆成了多个可观察、可替换、可测试的工程模块。

学习时应该不断追问：

1. 这个模块给模型增加了什么行动能力？
2. 它改变了上下文、工具、权限还是任务状态？
3. 如果缺少这个模块，agent 会在哪些场景下失败？
4. 这个模块能不能独立抽出来，用在自己的 agent 项目里？
