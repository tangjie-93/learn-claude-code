# `web` 项目结构说明

本文档用于快速理解 `web` 项目的整体结构、路由组织、数据流和主要模块职责。

## 项目定位

`web` 是一个基于 `Next.js 16`、`React 19`、`App Router` 的静态导出站点，用来展示 `Learn Claude Code` 课程。

它不是纯手写静态页面，而是通过 `scripts/extract-content.ts` 在 `dev` 和 `build` 前从仓库根目录的 `s01_...` 到 `s20_...` 课程章节中抽取内容，包括：

- `code_openai.py` 源码
- 多语言 `README.md`、`README.en.md`、`README.ja.md`
- 章节图片资源
- 代码中的 `LOC`、`tools`、`classes`、`functions`
- 相邻版本之间的差异信息

抽取后的数据会写入 `src/data/generated/`，再由前端页面和组件渲染。

## 顶层目录

```text
web/
├── src/
│   ├── app/                 # Next.js App Router 路由入口
│   ├── components/          # 页面组件、可视化、布局、UI 基础组件
│   ├── data/                # 静态数据：手写场景 + 生成内容
│   ├── hooks/               # 前端交互 hooks
│   ├── i18n/                # 多语言文案
│   ├── lib/                 # 常量、i18n helper、工具函数
│   └── types/               # Agent/课程数据类型定义
├── public/
│   └── course-assets/       # 构建前从章节 images 复制出来的课程图片
├── scripts/
│   └── extract-content.ts   # 内容抽取脚本
├── next.config.ts           # 静态导出配置
├── package.json             # 脚本和依赖
├── tsconfig.json            # TypeScript 配置
└── vercel.json              # Vercel 重定向配置
```

## 路由结构

核心路由位于 `src/app/`。

```text
src/app/
├── page.tsx
└── [locale]/
    ├── layout.tsx
    ├── page.tsx
    └── (learn)/
        ├── layout.tsx
        ├── timeline/page.tsx
        ├── compare/page.tsx
        ├── layers/page.tsx
        └── [version]/
            ├── page.tsx
            └── client.tsx
```

### 路由表

| 路由文件 | URL | 作用 |
| --- | --- | --- |
| `src/app/page.tsx` | `/` | 重定向到 `/en/` |
| `src/app/[locale]/page.tsx` | `/en/`、`/zh/`、`/ja/` | 首页，展示课程介绍、核心模式、学习路径、分层概览 |
| `src/app/[locale]/(learn)/timeline/page.tsx` | `/en/timeline/`、`/zh/timeline/`、`/ja/timeline/` | 时间线页面 |
| `src/app/[locale]/(learn)/compare/page.tsx` | `/en/compare/`、`/zh/compare/`、`/ja/compare/` | 版本对比页面 |
| `src/app/[locale]/(learn)/layers/page.tsx` | `/en/layers/`、`/zh/layers/`、`/ja/layers/` | 按能力层展示课程 |
| `src/app/[locale]/(learn)/[version]/page.tsx` | `/en/s01/` 到 `/en/s20/` 等 | 单个课程版本详情页 |

说明：

- `[locale]` 是动态语言段，目前支持 `en`、`zh`、`ja`。
- `[version]` 是动态课程版本段，对应 `s01` 到 `s20`。
- `(learn)` 是 `Next.js` 路由组目录，不会出现在 URL 中，只用于组织共享布局。

## 布局关系

### 全站语言布局

文件：`src/app/[locale]/layout.tsx`

职责：

- 通过 `generateStaticParams()` 生成 `en`、`zh`、`ja` 三种静态语言路径。
- 根据语言生成页面 `metadata`。
- 引入 `globals.css`。
- 注入深色模式初始化脚本。
- 包裹 `I18nProvider`。
- 渲染全站 `Header`。
- 提供统一的 `main` 内容容器。

### 学习区布局

文件：`src/app/[locale]/(learn)/layout.tsx`

职责：

- 渲染左侧 `Sidebar`。
- 渲染右侧主内容区。
- 作用范围包括：
  - `/[locale]/timeline/`
  - `/[locale]/compare/`
  - `/[locale]/layers/`
  - `/[locale]/[version]/`

首页 `/[locale]/` 不使用这个侧边栏布局。

## 页面职责

### 首页

文件：`src/app/[locale]/page.tsx`

职责：

- 展示 `Hero` 区域。
- 展示核心 `Agent Loop` 代码模式。
- 展示消息流可视化。
- 展示 `s01` 到 `s20` 学习路径入口。
- 展示 `LAYERS` 分层概览。

主要依赖：

- `LEARNING_PATH`
- `VERSION_META`
- `LAYERS`
- `src/data/generated/versions.json`
- `MessageFlow`
- `LayerBadge`
- `Card`

### 版本详情页

文件：

- `src/app/[locale]/(learn)/[version]/page.tsx`
- `src/app/[locale]/(learn)/[version]/client.tsx`

职责：

- `page.tsx` 是服务端页面，负责读取版本数据、差异数据、元信息和翻译。
- `client.tsx` 是客户端交互区，负责标签页和可视化交互。

页面中的主要标签页：

- `learn`：通过 `DocRenderer` 渲染 Markdown 文档。
- `simulate`：通过 `AgentLoopSimulator` 展示模拟器。
- `code`：通过 `SourceViewer` 展示源码。
- `deep-dive`：展示执行流、架构图、版本新增内容和设计决策。

### 时间线页面

文件：`src/app/[locale]/(learn)/timeline/page.tsx`

职责：

- 渲染课程学习时间线。
- 主要组件是 `components/timeline/timeline.tsx`。

### 对比页面

文件：`src/app/[locale]/(learn)/compare/page.tsx`

职责：

- 选择两个版本进行对比。
- 对比内容包括：
  - `LOC` 差异
  - 新增工具
  - 新增类
  - 新增函数
  - 工具交集和差集
  - 架构图对比
  - 代码差异

### 分层页面

文件：`src/app/[locale]/(learn)/layers/page.tsx`

职责：

- 按能力层展示课程章节。
- 每个层下面列出对应的 `sXX` 版本卡片。

分层数据来自 `src/lib/constants.ts` 中的 `LAYERS`。

## 核心数据流

```text
仓库根目录 s01_... ~ s20_...
        │
        ▼
web/scripts/extract-content.ts
        │
        ├── 读取 code_openai.py，提取 LOC / tools / classes / functions / source
        ├── 读取 README.md / README.en.md / README.ja.md
        ├── 重写 Markdown 中的图片路径和章节链接
        ├── 复制 images 到 public/course-assets/
        ▼
web/src/data/generated/
        ├── versions.json
        └── docs.json
        │
        ▼
Next.js 页面和组件渲染课程内容
```

## 数据目录

```text
src/data/
├── annotations/             # 每个版本的注释数据，s01.json 到 s20.json
├── scenarios/               # 每个版本的模拟器场景，s01.json 到 s20.json
├── generated/
│   ├── versions.json        # 自动生成：版本索引、源码、差异等
│   └── docs.json            # 自动生成：多语言 Markdown 文档
└── execution-flows.ts       # 执行流数据
```

### `versions.json`

由 `scripts/extract-content.ts` 生成，结构类型定义在 `src/types/agent-data.ts`。

主要包含：

- `versions`
  - `id`
  - `filename`
  - `title`
  - `subtitle`
  - `loc`
  - `tools`
  - `newTools`
  - `classes`
  - `functions`
  - `layer`
  - `source`
  - `images`
- `diffs`
  - `from`
  - `to`
  - `newClasses`
  - `newFunctions`
  - `newTools`
  - `locDelta`

### `docs.json`

由 `scripts/extract-content.ts` 生成。

主要包含：

- `version`
- `locale`
- `title`
- `content`

其中 `content` 是经过路径重写后的原始 Markdown。

## 常量配置

文件：`src/lib/constants.ts`

这是课程结构的核心配置源。

主要导出：

- `VERSION_ORDER`：版本顺序，`s01` 到 `s20`。
- `LEARNING_PATH`：学习路径，目前等同于 `VERSION_ORDER`。
- `VERSION_META`：每个版本的标题、副标题、核心新增点、关键洞察、所属层级、上一个版本。
- `LAYERS`：课程能力分层。

当前 `LAYERS` 包含：

| 层级 | 说明 | 版本 |
| --- | --- | --- |
| `tools` | `Tools & Execution` | `s01`、`s02`、`s03`、`s04` |
| `planning` | `Planning & Control` | `s05`、`s06`、`s07`、`s10`、`s11` |
| `memory` | `Memory Management` | `s08`、`s09` |
| `concurrency` | `Concurrency & Scheduling` | `s13`、`s14` |
| `collaboration` | `Multi-Agent Platform` | `s12`、`s15`、`s16`、`s17`、`s18`、`s19`、`s20` |

## 组件目录

```text
src/components/
├── architecture/            # 架构图、执行流、消息流、设计决策
├── code/                    # 源码展示
├── diff/                    # 代码差异和版本新增内容
├── docs/                    # Markdown 文档渲染
├── layout/                  # Header、Sidebar
├── simulator/               # Agent Loop 模拟器
├── timeline/                # 学习时间线
├── ui/                      # Badge、Card、Tabs 等基础 UI
└── visualizations/          # 每个版本的专题可视化组件
```

### `layout`

- `header.tsx`：顶部导航、语言切换、深色模式、GitHub 链接、移动端菜单。
- `sidebar.tsx`：学习区左侧导航，按 `LAYERS` 分组展示 `s01` 到 `s20`。

### `visualizations`

`visualizations/` 下按版本放置专题可视化组件，例如：

- `s01-agent-loop.tsx`
- `s02-tool-dispatch.tsx`
- `s03-permission.tsx`
- `s14-cron-scheduler.tsx`
- `s20-comprehensive.tsx`

入口文件是 `components/visualizations/index.tsx`，由版本详情页中的 `SessionVisualization` 调用。

## 国际化

```text
src/i18n/messages/
├── en.json
├── zh.json
└── ja.json
```

相关工具：

- `src/lib/i18n.tsx`：客户端 `I18nProvider`、`useTranslations`、`useLocale`。
- `src/lib/i18n-server.ts`：服务端 `getTranslations`。

语言路由：

- `/en/`
- `/zh/`
- `/ja/`

默认入口：

- `src/app/page.tsx` 将 `/` 重定向到 `/en/`。
- `vercel.json` 也配置了 `/` 到 `/en` 的重定向。

## 构建配置

### `package.json`

关键脚本：

```json
{
  "extract": "tsx scripts/extract-content.ts",
  "predev": "npm run extract",
  "dev": "next dev",
  "prebuild": "npm run extract",
  "build": "next build",
  "start": "next start"
}
```

含义：

- 执行 `npm run dev` 前会自动执行 `npm run extract`。
- 执行 `npm run build` 前也会自动执行 `npm run extract`。
- 因此 `src/data/generated/` 和 `public/course-assets/` 会在开发和构建前刷新。

### `next.config.ts`

```ts
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
};
```

含义：

- `output: "export"`：构建为静态站点。
- `images.unoptimized: true`：图片不走 `Next.js Image Optimization`。
- `trailingSlash: true`：生成带尾斜杠的路径。

## 添加新课程版本时要改哪里

如果要新增一个 `s21` 版本，通常需要：

1. 在仓库根目录新增章节目录，例如 `s21_xxx/`。
2. 在该目录中提供 `code_openai.py`。
3. 提供多语言文档：
   - `README.md`
   - `README.en.md`
   - `README.ja.md`
4. 如有图片，放入章节目录的 `images/`。
5. 在 `src/lib/constants.ts` 中更新：
   - `VERSION_ORDER`
   - `VERSION_META`
   - `LAYERS`
6. 如需模拟器，新增 `src/data/scenarios/s21.json`。
7. 如需注释，新增 `src/data/annotations/s21.json`。
8. 如需专题可视化，新增 `components/visualizations/s21-xxx.tsx`，并在 `components/visualizations/index.tsx` 中注册。
9. 运行 `npm run extract` 或直接运行 `npm run dev` / `npm run build`。

## 一句话理解

`web` 是一个以 `Next.js App Router` 为壳、以 `s01` 到 `s20` 课程章节为内容源、通过构建前脚本生成静态数据、再用多语言页面和交互组件展示的课程站点。
