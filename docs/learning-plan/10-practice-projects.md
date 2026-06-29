# 进阶实践项目

完成 30 天计划后，建议做三个小项目。

## 1. 实现一个 mini coding agent

### 最小功能

- `read_file`
- `write_file`
- `edit_file`
- `run_command`
- `todo_write`
- 简单危险命令拦截
- 简单 agent loop

### 目标

不用照抄项目代码，自己实现一版最小 harness。

### 验收方式

你的 mini agent 应该能完成：

1. 读取一个本地文件。
2. 修改一个本地文件。
3. 运行一个测试命令。
4. 记录并更新 todo。
5. 拒绝明显危险的命令。

## 2. 写一个自定义 skill

### 建议主题

- Vue 组件审查 skill
- TypeScript 类型检查 skill
- PR 总结 skill
- 测试生成 skill

### 目标

理解 skill 是如何把领域知识注入 agent 的。

### 验收方式

一个合格 skill 至少应该包含：

1. 适用场景。
2. 不适用场景。
3. 操作步骤。
4. 输出格式。
5. 质量检查标准。

## 3. 改造课程网站

### 可选任务

- 新增一个章节入口
- 新增一个可视化组件
- 修改 `extract-content.ts` 支持新的元数据字段
- 给某个章节增加新的 scenario

### 目标

理解课程内容如何从 Markdown / Python 代码流入前端 UI。

### 验收方式

完成后应该能说明：

1. 内容从哪个源文件进入前端。
2. 哪个脚本负责生成数据。
3. 哪个页面负责展示。
4. 哪个组件负责具体渲染。
