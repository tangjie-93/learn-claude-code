# 第 2 周：让 agent 更像工程工具

本周目标：理解 agent 如何管理任务、拆分职责、按需加载领域知识。

## Day 8：todo 管理

### 学习材料

- `s05_todo_write/code.py`

### 具体任务

1. 阅读 `TodoManager`。
2. 理解 todo 的状态字段。
3. 思考 todo 为什么不是普通聊天上下文。

### 产出

解释为什么 agent 需要显式 todo 状态。

## Day 9：todo 测试

### 学习材料

- `tests/test_todo_write_string_input.py`

### 具体任务

1. 阅读测试输入。
2. 找到测试期待的输出。
3. 理解字符串输入和结构化输入的差异。

### 产出

总结测试覆盖了哪些边界。

## Day 10：subagent

### 学习材料

- `s06_subagent/code.py`

### 具体任务

1. 找到 `run_subagent`。
2. 理解主 agent 如何调用 subagent。
3. 判断 subagent 是否共享主上下文。

### 产出

说明 subagent 与主 agent 的上下文隔离方式。

## Day 11：subagent 练习

### 具体任务

设计一个 code-review subagent prompt。

需要包含：

- 角色
- 输入
- 输出格式
- 不允许做什么
- 何时返回阻塞问题

### 产出

写出完整 subagent prompt 草稿。

## Day 12：skill loading

### 学习材料

- `s07_skill_loading/code.py`

### 具体任务

1. 阅读 `SkillLoader`。
2. 找到 skill 发现逻辑。
3. 理解 skill 如何进入 system prompt 或上下文。

### 产出

解释 SkillLoader 如何发现和加载技能。

## Day 13：skill 文件结构

### 学习材料

- `skills/agent-builder/SKILL.md`
- `skills/code-review/SKILL.md`

### 具体任务

1. 阅读两个 skill 文件。
2. 对比它们的结构。
3. 总结一个可复用 skill 应该包含哪些信息。

### 产出

写出 “好 skill 的 5 个标准”。

## Day 14：第 2 周复盘

### 具体任务

对比 todo、subagent、skill。

### 产出

写一张职责边界表：

| 模块 | 解决的问题 | 不应该承担的职责 |
| --- | --- | --- |
