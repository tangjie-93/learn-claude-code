# 代码图谱

本文档从代码结构层面梳理本仓库。它是刻意保持静态并纳入源码管理的文档，方便随代码一起审查，并在目录结构或主要依赖发生变化时更新。

## 仓库概览

```mermaid
flowchart TD
  Root["仓库根目录"]
  Readmes["README*.md / CONTRIBUTING.md / LICENSE"]
  ChapterDirs["s01_* ... s20_* 章节目录"]
  ChapterDocs["章节 README 文件"]
  ChapterCode["章节 code.py 示例"]
  ChapterImages["章节 images/*.svg"]
  Agents["agents/ 汇总版 Python 实现"]
  Tests["tests/ Python 行为测试和冒烟测试"]
  Skills["skills/ 本地技能示例"]
  Docs["docs/{en,zh,ja}/ 长篇章节文档"]
  Web["web/ Next.js 课程 UI"]

  Root --> Readmes
  Root --> ChapterDirs
  Root --> Agents
  Root --> Tests
  Root --> Skills
  Root --> Docs
  Root --> Web

  ChapterDirs --> ChapterDocs
  ChapterDirs --> ChapterCode
  ChapterDirs --> ChapterImages

  ChapterCode --> WebExtract["web/scripts/extract-content.ts"]
  Docs --> WebExtract
  ChapterImages --> WebExtract
  Agents --> Tests
  ChapterCode --> Tests
  Skills --> ChapterCode
```

## Python Agent 代码

根目录下的 `sXX_*/code.py` 文件是各章节示例。`agents/` 目录包含命名相近的汇总版实现，供测试使用，也方便希望在一个位置查看所有版本的读者阅读。

```mermaid
flowchart LR
  S01["s01 agent 循环\nrun_bash + agent_loop"]
  S02["s02 工具使用\nread/write/edit + safe_path"]
  S03["s03 todo 写入\nTodoManager"]
  S04["s04 子 agent\nrun_subagent"]
  S05["s05 技能加载\nSkillLoader"]
  S06["s06 上下文压缩\n微压缩/自动压缩"]
  S07["s07 任务系统\nTaskManager"]
  S08["s08 后台任务\nBackgroundManager"]
  S09["s09 agent 团队\nMessageBus + TeammateManager"]
  S10["s10 团队协议\n关闭 + 计划审查"]
  S11["s11 自主 agent\n任务扫描/领取 + 身份"]
  S12["s12 worktree 隔离\nEventBus + WorktreeManager"]
  Full["agents/s_full.py\n组合测试框架"]

  S01 --> S02 --> S03 --> S04 --> S05 --> S06 --> S07 --> S08 --> S09 --> S10 --> S11 --> S12
  S03 --> Full
  S05 --> Full
  S06 --> Full
  S07 --> Full
  S08 --> Full
  S09 --> Full
  S10 --> Full
```

### 共享 Python 运行时依赖

```mermaid
flowchart TD
  AgentLoop["agent_loop(messages)"]
  Anthropic["Anthropic 客户端"]
  Tools["TOOLS schema"]
  ToolDispatch["工具分发"]
  Shell["subprocess shell"]
  FS["文件系统辅助函数"]
  Env[".env / MODEL_ID / ANTHROPIC_*"]
  Managers["功能管理器\nTodo / Skill / Task / Background / Team"]

  Env --> Anthropic
  AgentLoop --> Anthropic
  AgentLoop --> Tools
  Anthropic --> ToolDispatch
  ToolDispatch --> Shell
  ToolDispatch --> FS
  ToolDispatch --> Managers
  Shell --> AgentLoop
  FS --> AgentLoop
  Managers --> AgentLoop
```

### Python 测试覆盖图

```mermaid
flowchart TD
  Tests["tests/"]
  Smoke["test_agents_smoke.py"]
  Todo["test_todo_write_string_input.py"]
  Compact["test_compaction_tool_pairs.py"]
  Background["test_s_full_background.py"]
  AgentFiles["agents/*.py"]
  SFull["agents/s_full.py"]
  S03["s03_todo_write / TodoManager 行为"]
  S06["上下文压缩工具对"]
  S08["后台任务行为"]

  Tests --> Smoke --> AgentFiles
  Tests --> Todo --> S03
  Tests --> Compact --> S06
  Tests --> Background --> SFull
  SFull --> S08
```

## Web 应用代码

`web/` 应用是一个 Next.js UI，用于渲染课程、代码、架构图、模拟器和 diff。构建命令和开发命令会先运行 `web/scripts/extract-content.ts`，该脚本会从仓库中复制/提取源材料，并生成 JSON 与 public 资源。

```mermaid
flowchart TD
  Next["Next.js app router\nweb/src/app"]
  LocaleLayout["[locale]/layout.tsx\nI18nProvider + Header"]
  Home["[locale]/page.tsx\n课程首页"]
  LearnLayout["(learn)/layout.tsx\nSidebar"]
  VersionPage["(learn)/[version]/page.tsx\n服务端数据加载"]
  VersionClient["(learn)/[version]/client.tsx\n标签页和详情 UI"]
  DiffPage["(learn)/[version]/diff"]
  ComparePage["(learn)/compare"]
  LayersPage["(learn)/layers"]
  TimelinePage["(learn)/timeline"]

  Next --> LocaleLayout
  LocaleLayout --> Home
  LocaleLayout --> LearnLayout
  LearnLayout --> VersionPage --> VersionClient
  LearnLayout --> DiffPage
  LearnLayout --> ComparePage
  LearnLayout --> LayersPage
  LearnLayout --> TimelinePage
```

### Web 组件图

```mermaid
flowchart TD
  VersionClient["VersionDetailClient"]
  Tabs["ui/Tabs"]
  DocRenderer["docs/DocRenderer"]
  SourceViewer["code/SourceViewer"]
  Simulator["simulator/AgentLoopSimulator"]
  SessionViz["visualizations/SessionVisualization"]
  ExecutionFlow["architecture/ExecutionFlow"]
  ArchDiagram["architecture/ArchDiagram"]
  WhatsNew["diff/WhatsNew"]
  DesignDecisions["architecture/DesignDecisions"]
  StepViz["visualizations/sXX-*"]
  SharedViz["visualizations/shared\nStepControls / MechanismFlow"]
  Hooks["hooks\nuseSimulator / useSteppedVisualization / useDarkMode"]
  UI["ui\nCard / Badge / Tabs"]

  VersionClient --> Tabs
  VersionClient --> DocRenderer
  VersionClient --> SourceViewer
  VersionClient --> Simulator
  VersionClient --> SessionViz
  VersionClient --> ExecutionFlow
  VersionClient --> ArchDiagram
  VersionClient --> WhatsNew
  VersionClient --> DesignDecisions

  SessionViz --> StepViz
  StepViz --> SharedViz
  StepViz --> Hooks
  Simulator --> Hooks
  DocRenderer --> UI
  DesignDecisions --> UI
  WhatsNew --> UI
```

### Web 数据流水线

```mermaid
flowchart LR
  RootChapters["根目录 sXX_* 目录\nREADME + code.py + images"]
  RootDocs["docs/{en,zh,ja}/*.md"]
  AgentSource["agents/*.py"]
  Extract["web/scripts/extract-content.ts"]
  GeneratedVersions["web/src/data/generated/versions.json"]
  GeneratedDocs["web/src/data/generated/docs.json"]
  PublicAssets["web/public/course-assets/"]
  StaticData["web/src/data\nannotations / scenarios / execution-flows"]
  Components["web/src/components"]

  RootChapters --> Extract
  RootDocs --> Extract
  AgentSource --> Extract
  Extract --> GeneratedVersions
  Extract --> GeneratedDocs
  Extract --> PublicAssets
  GeneratedVersions --> Components
  GeneratedDocs --> Components
  PublicAssets --> Components
  StaticData --> Components
```

## 重要模块职责

| 区域 | 路径 | 职责 |
| --- | --- | --- |
| Python 章节示例 | `s01_*` 到 `s20_*` | 每章对应的源码、README 内容和图表。 |
| 汇总版 agent 实现 | `agents/` | 独立 Python 版本，以及组合测试框架 `s_full.py`。 |
| 测试 | `tests/` | 冒烟检查，以及针对 todo、压缩和后台任务功能的聚焦行为测试。 |
| 内容提取 | `web/scripts/extract-content.ts` | 基于根目录文档、代码和资源构建生成的 Web 数据。 |
| Next 路由 | `web/src/app/` | 支持 locale 的应用页面和版本详情路由。 |
| 课程 UI 组件 | `web/src/components/` | 架构、文档、代码查看器、模拟器、时间线、diff 和可视化组件。 |
| 共享前端状态 | `web/src/hooks/` | 模拟器步进、可视化步进，以及暗色模式/SVG 调色板行为。 |
| 静态前端数据 | `web/src/data/` | 生成的版本/文档，以及手写的场景、注解和流程定义。 |
| 本地化 | `web/src/i18n/messages/` 和 `web/src/lib/i18n*.ts*` | 英文、中文和日文消息，以及运行时/服务端翻译辅助函数。 |

## 更新检查清单

添加主要功能或目录时，如果以下任一内容发生变化，请更新此图谱：

- 出现新的顶层代码区域。
- 某个章节新增运行时管理器或主要工具类别。
- `web/scripts/extract-content.ts` 开始生成新的产物。
- `web/src/app` 或 `web/src/components` 下新增页面组或主要组件家族。
- 测试开始覆盖新的子系统。
