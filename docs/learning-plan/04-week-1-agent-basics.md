# 第 1 周：建立 agent 基础模型

本周目标：理解最小 `coding agent` 是如何工作的。重点是 `agent loop`、工具调用、权限控制和 `hooks`。

## Day 1：项目总览

### 学习材料

- `README-zh.md`
- `docs/code-graph.md`
- `docs/learning-plan/01-project-positioning.md`
- `docs/learning-plan/02-code-structure.md`

### 具体任务

1. 浏览项目顶层目录。
2. 标出 `Python` 示例、课程文档、前端网站三个区域。
3. 阅读 code graph，理解项目依赖关系。

### 产出

写下：

- 项目三大模块是什么
  - agents
  - test
  - web
- 课程主线是什么
  - `coding agent`
- 你最不理解的 3 个概念是什么
  - 目前还没有

## Day 2：最小 `agent loop`

### 学习材料

- `s01_agent_loop/code.py`
- `agents/s01_agent_loop.py`

### 具体任务

1. 找到 `agent_loop(messages)`。
2. 找到 `run_bash(command)`。
3. 理解模型返回 `tool_use` 后，代码如何执行工具。
4. 理解工具结果如何作为 `tool_result` 放回 `messages`。

### 产出

画出这个流程：

```text
user message
  -> model
  -> tool_use
  -> run tool
  -> tool_result
  -> model
  -> final answer
```

## Day 3：工具调用系统

### 学习材料

- `s02_tool_use/code.py`
- `agents/s02_tool_use.py`

### 具体任务

1. 阅读工具 schema。
2. 对比 `bash`、`read`、`write`、`edit` 四类工具。
3. 找到 `safe_path` 并理解路径限制。

### 产出

写出一张表：

| 工具     | 输入     | 输出     | 风险     | 防护     |
| ------ | ------ | ------ | ------ | ------ |
| <br /> | <br /> | <br /> | <br /> | <br /> |

## Day 4：工具扩展练习

### 具体任务

设计一个 `list_files` 工具，不要求提交代码，但要写出：

1. 工具 schema。
2. 执行函数签名。
3. 路径安全策略。
4. 返回值格式。

### 产出

写出 `list_files` 的最小设计草稿。

## Day 5：权限控制

### 学习材料

- `s03_permission/code.py`
- `s03_permission/README.md`

### 具体任务

1. 找到危险操作判断逻辑。
2. 理解哪些操作应该被拦截。
3. 思考权限系统是工具层能力，还是模型层能力。

### 产出

总结：

- 哪些操作需要拦截
- 为什么只靠 prompt 不够
- 权限检查应该放在哪一层

## Day 6：`hooks` 机制

### 学习材料

- `s04_hooks/code.py`
- `s04_hooks/README.md`

### 具体任务

1. 找到 `hook` 的调用点。
2. 区分 `before hook` 和 `after hook`。
3. 思考 `hook` 可以用于日志、安全、格式化、测试等哪些场景。

### 产出

写出 `3` 个 `hook` 使用场景。

## Day 7：第 1 周复盘

### 具体任务

回顾 `s01` 到 `s04`。

### 产出

写一页总结：

- 最小 `coding agent` 需要哪些模块
- 工具系统和权限系统如何协作
- `hooks` 给 harness 带来了什么扩展能力

