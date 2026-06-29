# 学习目标

完成 30 天学习后，应该达到以下水平：

1. 能完整解释一个 coding agent 的核心循环。
2. 能设计和实现基本工具系统，包括 read、write、edit、bash。
3. 能理解工具调用、工具结果、上下文历史之间的关系。
4. 能实现简单权限拦截和 hooks。
5. 能解释 todo、task system、background task 的区别。
6. 能理解 subagent 和 skill 的边界。
7. 能说明 context compact 为什么必须保护 tool_use/tool_result 配对。
8. 能读懂 `agents/s_full.py` 的整体结构。
9. 能基于该项目实现一个自己的 mini coding agent harness。

## 阶段性目标

### 第 1 周结束

你应该能说明：

- agent loop 的最小结构
- tool_use 和 tool_result 的关系
- 工具系统如何接入模型调用
- 权限和 hooks 为什么必须存在

### 第 2 周结束

你应该能说明：

- todo 为什么是 agent 的外部工作记忆
- subagent 如何做职责隔离
- skill 如何把领域知识按需加载
- 工具、todo、subagent、skill 的职责边界

### 第 3 周结束

你应该能说明：

- 上下文为什么会膨胀
- compact 的风险是什么
- memory 和 context 的区别
- system prompt 在 harness 中承担哪些策略

### 第 4 周结束

你应该能说明：

- task system 如何支撑长期任务
- background task 和普通工具调用的区别
- agent team 如何通信和协作
- worktree isolation 和 MCP plugin 解决什么扩展问题
