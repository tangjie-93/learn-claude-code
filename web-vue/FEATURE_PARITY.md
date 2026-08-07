# `web-vue` Feature Parity Notes

This document tracks the migration from the original `web/` `Next.js` application to the new `Vue 3` implementation.

## Implemented

- `Vue 3 + TypeScript + Vue Router + Pinia + Less + Vite` project structure.
- Locale routes:
  - `/`
  - `/:locale`
  - `/:locale/timeline`
  - `/:locale/compare`
  - `/:locale/layers`
  - `/:locale/:version`
- Reused generated course data:
  - `src/data/generated/versions.json`
  - `src/data/generated/docs.json`
  - `src/data/scenarios/*.json`
  - `src/data/annotations/*.json`
  - `public/course-assets/**`
- Course source extraction uses `code_openai.py` for version metadata and source display.
- Route-level lazy loading plus on-demand generated course data loading.
- Version detail hero visualizations are wired through `SessionVisualization` with per-version lazy chunks.
- Migrated complete visualization set:
  - `s01` Agent Loop
  - `s02` Tool Dispatch
  - `s03` Permission
  - `s04` Hooks
  - `s05` TodoWrite
  - `s06` Subagent
  - `s07` Skill Loading
  - `s08` Context Compact
  - `s09` Memory
  - `s10` System Prompt
  - `s11` Error Recovery
  - `s12` Task System
  - `s13` Background Tasks
  - `s14` Cron Scheduler
  - `s15` Agent Teams
  - `s16` Team Protocols
  - `s17` Autonomous Agents
  - `s18` Worktree Isolation
  - `s19` MCP Tools
  - `s20` Comprehensive
- Home page learning path and layer overview.
- Sidebar grouped by learning layer.
- Version detail tabs:
  - Learn
  - Simulate
  - Code
  - Deep Dive
- `Markdown` rendering through `unified`, `remark-gfm`, `rehype-raw`, `rehype-highlight`.
- Simulator playback state:
  - Play
  - Pause
  - Step
  - Reset
  - Speed selection
- Timeline:
  - Layer legend
  - Version cards
  - `LOC` growth meters
- Compare page:
  - Version selection
  - `LOC` delta
  - New tools/classes/functions
  - Tool-only/shared comparison
  - Unified and split code diff view
- Deep dive:
  - Execution flow SVG map
  - Architecture class stack
  - What changed summary
  - Design decisions from annotations
- Responsive header with mobile menu, locale switching, and theme actions.

## Tested

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

## Remaining Gaps

- Original `Framer Motion` animations are replaced by static `Vue`/`Less` layouts.
- `VersionView` and generated data chunks are still large; they can be split further by tab/component or per-version data files.
