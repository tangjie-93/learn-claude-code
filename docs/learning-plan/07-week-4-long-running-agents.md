# 第 4 周：任务系统、多 agent 和长期运行

本周目标：理解 agent 如何从一次性工具调用，扩展为可以处理长期任务、后台任务和团队协作的系统。

## Day 22：错误恢复

### 学习材料

- `s11_error_recovery/code.py`

### 具体任务

1. 找到错误捕获和恢复逻辑。
2. 区分工具错误、模型错误、流程错误。
3. 思考恢复策略是否应该自动执行。

### 产出

总结错误恢复和普通异常处理的区别。

## Day 23：`task system`

### 学习材料

- `s12_task_system/code.py`

### 具体任务

1. 阅读 `TaskManager`。
2. 找到任务创建、更新、完成逻辑。
3. 画出任务状态流转。

### 产出

画出 TaskManager 状态流转图。

## Day 24：`background tasks`

### 学习材料

- `s13_background_tasks/code.py`

### 具体任务

1. 阅读 `BackgroundManager`。
2. 理解后台任务如何启动。
3. 理解任务结果如何查询。

### 产出

解释后台任务如何创建、查询和回收。

## Day 25：background 测试

### 学习材料

- `tests/test_s_full_background.py`

### 具体任务

1. 阅读测试如何构造后台任务。
2. 找到成功、失败、查询状态相关断言。

### 产出

总结后台任务测试点。

## Day 26：`cron` `scheduler`

### 学习材料

- `s14_cron_scheduler/code.py`

### 具体任务

1. 理解定时任务表示方式。
2. 找到调度触发逻辑。
3. 思考 `cron` 和 `background task` 的关系。

### 产出

说明定时任务如何扩展 agent 行为。

## Day 27：`agent teams`

### 学习材料

- `s15_agent_teams/code.py`

### 具体任务

1. 阅读 `MessageBus`。
2. 阅读 `TeammateManager`。
3. 理解 team 内部通信方式。

### 产出

解释 MessageBus 和 TeammateManager 的职责。

## Day 28：team `protocols`

### 学习材料

- `s16_team_protocols/code.py`

### 具体任务

1. 找到计划审查逻辑。
2. 找到 shutdown 协议。
3. 理解团队协作中为什么需要协议。

### 产出

总结计划审查、关闭协议和协作约束。

## Day 29：高级主题通读

### 学习材料

- `s17_autonomous_agents/code.py`
- `s18_worktree_isolation/code.py`
- `s19_mcp_plugin/code.py`
- `s20_comprehensive/code.py`

### 具体任务

1. 快速阅读，不逐行深挖。
2. 记录每章新增能力。
3. 标记需要二刷的模块。

### 产出

记录 autonomous agents、`worktree`、`MCP`、comprehensive 的关键点。

## Day 30：总复盘

### 学习材料

- `agents/s_full.py`

### 具体任务

1. 阅读完整 harness。
2. 标记每个模块来自前面哪一章。
3. 画出完整架构图。

### 产出

完成一张完整 `agent harness` 架构图。
