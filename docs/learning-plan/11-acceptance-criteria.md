# 最终验收标准

学习完成后，至少应该能交付以下成果：

1. 一张完整 `agent harness` 架构图。
2. 一份 `s01` 到 `s20` 的能力演进表。
3. 一个自己实现的 `mini coding agent`。
4. 一个自定义 `skill`。
5. 一篇总结文档：`我理解的 Coding Agent Harness`。

## 能力验收问题

你应该能独立回答：

1. `agent loop` 的最小闭环是什么？
2. `tool schema` 为什么重要？
3. `tool_use` 和 `tool_result` 为什么必须成对出现？
4. 权限检查为什么不能只靠 `system prompt`？
5. `hooks` 适合解决什么问题？
6. `todo` 和 `task system` 的区别是什么？
7. `subagent` 解决的是上下文问题，还是并发问题？
8. `skill` loading 和 `memory` 的区别是什么？
9. `context compact` 最大的风险是什么？
10. `background task` 为什么不能简单等同于普通 tool call？
11. agent team 为什么需要 MessageBus？
12. `worktree isolation` 解决什么工程冲突？
13. `MCP plugin` 扩展的是哪一层能力？

## 最终判断

如果能做到这些，就不是“看过这个项目”，而是真正掌握了它的工程思想。
