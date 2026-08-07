# Web Vue Next Visual Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `web-vue` visually match the original `web/` Next.js pages as closely as practical without rewriting the app stack.

**Architecture:** Keep the existing Vue Router, Pinia data store, generated data, and component boundaries. Translate missing Next.js page structure and Tailwind visual contracts into focused Vue components and `main.less` styles.

**Tech Stack:** Vue 3, TypeScript, Pinia, Vue Router, Less, Vite, Vitest.

---

### Task 1: Restore Original Page Structure

**Files:**
- Create: `web-vue/src/components/MessageFlow.vue`
- Modify: `web-vue/src/views/HomeView.vue`
- Modify: `web-vue/src/views/VersionView.vue`

- [ ] Add a Vue `MessageFlow` component matching the original `web/src/components/architecture/message-flow.tsx`.
- [ ] Insert original homepage sections in this order: hero, core pattern, message flow, learning path, layer overview.
- [ ] Remove the extra Vue-only version heading so version detail pages start with `SessionVisualization`, then tabs.

### Task 2: Align Global Visual Contract

**Files:**
- Modify: `web-vue/src/styles/main.less`
- Modify: `web-vue/src/components/AppHeader.vue` if needed

- [ ] Match original `web/src/app/globals.css` variables: `--color-bg`, `--color-bg-secondary`, `--color-text`, `--color-text-secondary`, `--color-border`.
- [ ] Translate original header, sidebar, cards, tabs, section spacing, and responsive rules.
- [ ] Keep existing custom visualization styles but normalize container spacing and cards to original radius/padding/color.

### Task 3: Verify and Iterate

**Files:**
- Modify only files with visible mismatches after screenshots.

- [ ] Run `npm run test` in `web-vue`.
- [ ] Run `npm run build` in `web-vue`.
- [ ] Start `web` and `web-vue` dev servers.
- [ ] Capture comparable desktop and mobile screenshots for `/en`, `/en/s01`, `/en/timeline`, `/en/compare`, and `/en/layers`.
- [ ] Patch remaining mismatches found in screenshots.
