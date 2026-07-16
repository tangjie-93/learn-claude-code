# 代码结构分析

## 1. 根目录章节

根目录下的 `s01_*` 到 `s20_*` 是课程主体。每个章节目录通常包含：

- `README.md`
- `README.en.md`
- `README.ja.md`
- `code.py`
- `images/*.svg`

这些目录适合按顺序学习。`code.py` 是每章最重要的代码入口。

## 2. `agents/`

`agents/` 目录包含集中版 `Python` agent 实现：

- `s01_agent_loop.py`
- `s02_tool_use.py`
- ...
- `s12_worktree_task_isolation.py`
- `s_full.py`

其中 `s_full.py` 是综合版本，适合在学完前面章节后阅读，用来理解完整 harness 如何组合。

## 3. `tests/`

测试目录用于验证关键行为：

- `test_agents_smoke.py`：基础编译和 `smoke test`
- `test_todo_write_string_input.py`：`todo` 输入行为
- `test_compaction_tool_pairs.py`：上下文压缩时 `tool_use/tool_result` 配对
- `test_s_full_background.py`：后台任务行为

学习时不要跳过测试。测试能帮助理解哪些行为是项目作者认为必须保证的。

## 4. `web/`

`web/` 是一个 `Next.js` 应用，用于展示课程内容。关键路径：

- `web/src/app/`：`Next.js` app router 页面
- `web/src/components/`：课程 `UI`、代码展示、模拟器、架构图、可视化组件
- `web/src/data/`：场景、注释、执行流程和生成数据
- `web/scripts/extract-content.ts`：从根目录章节、文档和代码中抽取内容，生成前端数据

如果主要目标是学习 `agent harness`，先学 `Python` 主线；如果目标还包括课程平台或可视化系统，再深入 `web/`。

## 建议阅读顺序

1. `README-zh.md`
2. `docs/code-graph.md`
3. `s01_agent_loop/code.py`
4. `s02_tool_use/code.py`
5. 对应章节的中文文档
6. `agents/s_full.py`
7. `web/scripts/extract-content.ts`
8. `web/src/app` 和 `web/src/components`
