# `web-vue` 功能对齐说明

本文档用于记录从原始 `web/` `Next.js` 应用迁移到新版 `Vue 3` 实现的功能对齐情况。

## 已实现

- 已搭建 `Vue 3 + TypeScript + Vue Router + Pinia + Less + Vite` 项目结构。
- 已实现本地化路由：
  - `/`
  - `/:locale`
  - `/:locale/timeline`
  - `/:locale/compare`
  - `/:locale/layers`
  - `/:locale/:version`
- 已复用生成后的课程数据：
  - `src/data/generated/versions.json`
  - `src/data/generated/docs.json`
  - `src/data/scenarios/*.json`
  - `src/data/annotations/*.json`
  - `public/course-assets/**`
- 课程源码提取使用 `code_openai.py`，用于版本元数据和源码展示。
- 已实现路由级懒加载，以及生成课程数据的按需加载。
- 版本详情页顶部可视化通过 `SessionVisualization` 接入，并按版本拆分为懒加载 chunk。
- 已迁移完整可视化组件集：
  - `s01` `Agent Loop`
  - `s02` `Tool Dispatch`
  - `s03` `Permission`
  - `s04` `Hooks`
  - `s05` `TodoWrite`
  - `s06` `Subagent`
  - `s07` `Skill Loading`
  - `s08` `Context Compact`
  - `s09` `Memory`
  - `s10` `System Prompt`
  - `s11` `Error Recovery`
  - `s12` `Task System`
  - `s13` `Background Tasks`
  - `s14` `Cron Scheduler`
  - `s15` `Agent Teams`
  - `s16` `Team Protocols`
  - `s17` `Autonomous Agents`
  - `s18` `Worktree Isolation`
  - `s19` `MCP Tools`
  - `s20` `Comprehensive`
- 已实现首页学习路径和分层概览。
- 已实现按学习层级分组的侧边栏。
- 已实现版本详情页标签页：
  - `Learn`
  - `Simulate`
  - `Code`
  - `Deep Dive`
- `Markdown` 渲染使用 `unified`、`remark-gfm`、`rehype-raw`、`rehype-highlight`。
- 已实现模拟器播放状态：
  - `Play`
  - `Pause`
  - `Step`
  - `Reset`
  - 速度选择
- 已实现时间线页面：
  - 分层图例
  - 版本卡片
  - `LOC` 增长条
- 已实现对比页面：
  - 版本选择
  - `LOC` 差异
  - 新增工具、类、函数
  - 仅工具和共享工具对比
  - 统一视图和分栏视图代码 diff
- 已实现深度解析内容：
  - 执行流 `SVG` 图
  - 架构类栈
  - 变更摘要
  - 来自注解数据的设计决策
- 已实现响应式顶部导航，包括移动端菜单、语言切换和主题操作。

## 已测试

- `src/utils/markdown.test.ts`
- `src/composables/simulator.test.ts`
- `src/utils/learning.test.ts`
- `src/utils/compare.test.ts`
- `src/utils/deep-dive.test.ts`
- `src/utils/code-diff.test.ts`
- `src/utils/flow-layout.test.ts`
- `src/components/AppHeader.test.ts`
- `src/stores/app.test.ts`
- `src/composables/stepped-visualization.test.ts`
- `src/components/SessionVisualization.test.ts`
- `src/components/SessionVisualization.loaders.test.ts`
- `src/components/visualizations/S01AgentLoop.test.ts`
- `src/components/visualizations/S02ToolDispatch.test.ts`
- `src/components/visualizations/S03Permission.test.ts`
- `src/components/visualizations/S04Hooks.test.ts`
- `src/components/visualizations/S05TodoWrite.test.ts`
- `src/components/visualizations/S06Subagent.test.ts`
- `src/components/visualizations/S07SkillLoading.test.ts`
- `src/components/visualizations/S08ContextCompact.test.ts`
- `src/components/visualizations/S09Memory.test.ts`
- `src/components/visualizations/S10SystemPrompt.test.ts`
- `src/components/visualizations/S11ErrorRecovery.test.ts`
- `src/components/visualizations/S12TaskSystem.test.ts`
- `src/components/visualizations/S13BackgroundTasks.test.ts`
- `src/components/visualizations/S14CronScheduler.test.ts`
- `src/components/visualizations/S15AgentTeams.test.ts`
- `src/components/visualizations/S16TeamProtocols.test.ts`
- `src/components/visualizations/S17AutonomousAgents.test.ts`
- `src/components/visualizations/S18WorktreeIsolation.test.ts`
- `src/components/visualizations/S19McpTools.test.ts`
- `src/components/visualizations/S20Comprehensive.test.ts`
- `src/views/VersionView.test.ts`
- `tests/structure.test.mjs`

## 剩余差距

- 原版 `Framer Motion` 动画已替换为静态 `Vue`/`Less` 布局。
- `VersionView` 和生成数据 chunk 仍然偏大，后续可以继续按标签页、组件或单版本数据文件进一步拆分。
