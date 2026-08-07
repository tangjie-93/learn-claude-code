<template>
  <section class="memory-vis" data-testid="s09-memory">
    <h2>{{ title || "Memory Library" }}</h2>

    <div class="memory-stage">
      <div class="phase-strip">
        <div v-for="(phase, index) in phases" :key="phase" :class="['phase-pill', { active: isPhaseActive(index) }]">
          {{ index + 1 }}. {{ phase }}
        </div>
      </div>

      <div class="session-grid">
        <article :class="surfaceClass(currentStep <= 2)">
          <div class="surface-head">
            <span :class="['surface-icon', { active: currentStep <= 2 }]">IN</span>
            <span>Session A: learn</span>
          </div>

          <div class="surface-body">
            <div class="quote-card">"Please keep LCC pages concrete for beginners."</div>

            <Transition name="fade-up">
              <div v-if="currentStep >= 1" class="stamp-card">
                <div>Memory extractor stamp</div>
                <p>Save a durable preference after the useful work is done.</p>
              </div>
            </Transition>

            <Transition name="fade-up">
              <MemoryDetail v-if="currentStep >= 2" :file="selectedFile" :selected="false" />
            </Transition>
          </div>
        </article>

        <article :class="surfaceClass(futureVisible)">
          <div class="surface-head">
            <span :class="['surface-icon', { active: futureVisible }]">{{ selected ? "SR" : "AI" }}</span>
            <span>Session B: recall</span>
          </div>

          <div class="surface-body">
            <EmptyState v-if="!futureVisible" label="future request has not arrived" />
            <div v-else class="quote-card">"Continue improving the web lesson visuals."</div>

            <Transition name="fade-up">
              <div v-if="selected" class="search-card">
                Catalog search selects <span class="mono">lcc_visual_preference.md</span>
              </div>
            </Transition>

            <Transition name="fade-up">
              <div v-if="injected" class="reading-stack">
                <div class="stack-title">Reading stack before LLM</div>
                <div class="stack-items">
                  <div class="stack-item current">current request</div>
                  <div class="stack-item memory">selected memory detail</div>
                  <Transition name="fade-up">
                    <div v-if="currentStep >= 7" class="stack-item answer">
                      answer keeps the user's preference
                    </div>
                  </Transition>
                </div>
              </div>
            </Transition>
          </div>
        </article>
      </div>

      <article :class="['surface-card', 'library-card', { active: catalogVisible || selected }]">
        <div class="surface-head">
          <span :class="['surface-icon', { active: catalogVisible || selected }]">BK</span>
          <span>.memory library</span>
        </div>

        <div class="library-grid">
          <div class="catalog-panel">
            <div class="catalog-head">
              <span>DOC</span>
              <span>MEMORY.md catalog</span>
            </div>

            <div class="catalog-list">
              <CatalogRow
                v-for="(file, index) in memoryFiles"
                :key="file.id"
                :file="file"
                :visible="catalogVisible && (index === 0 || currentStep >= 4)"
                :selected="selected && file.relevant === true"
              />
              <EmptyState v-if="!catalogVisible" label="catalog has not been rebuilt yet" />
            </div>
          </div>

          <div class="preview-panel">
            <div class="preview-title">Memory file preview</div>

            <div v-if="currentStep >= 2" class="preview-grid">
              <MemoryDetail :file="selectedFile" :selected="selected" />

              <div class="unloaded-list">
                <div v-for="file in unloadedFiles" :key="file.id" class="unloaded-card">
                  <div class="unloaded-head">
                    <span>{{ file.title }}</span>
                    <span :class="['type-pill', typeClass(file.type)]">not loaded</span>
                  </div>
                  <p>{{ file.description }}</p>
                </div>
              </div>
            </div>

            <EmptyState v-else label="no files on the shelf yet" />
          </div>
        </div>
      </article>

      <div class="beginner-rule">
        Beginner rule: the catalog stays cheap and readable; full memory files are borrowed only when the current
        request needs them.
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="current.title"
        :step-description="current.desc"
        @prev="prev"
        @next="next"
        @reset="reset"
        @toggle="toggleAutoPlay"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type MemoryType = "feedback" | "project" | "reference";

interface MemoryFile {
  id: string;
  type: MemoryType;
  title: string;
  filename: string;
  description: string;
  body: string;
  relevant?: boolean;
}

defineProps<{
  title?: string;
}>();

const memoryFiles: MemoryFile[] = [
  {
    id: "visual-preference",
    type: "feedback",
    title: "Beginner visual preference",
    filename: "lcc_visual_preference.md",
    description: "Use concrete mental models for LCC web pages.",
    body: "Prefer cards, boards, shelves, and workbenches over abstract flowcharts.",
    relevant: true,
  },
  {
    id: "project-path",
    type: "project",
    title: "LCC web paths",
    filename: "lcc_web_paths.md",
    description: "Web app reads root lesson folders and generated JSON.",
    body: "Build from web/, extract content from s01-s20 lesson directories.",
  },
  {
    id: "test-command",
    type: "reference",
    title: "Verification commands",
    filename: "lcc_test_commands.md",
    description: "Useful smoke checks for the course website.",
    body: "Run npm run build, then browser-check /zh/s09 and /zh/s20.",
  },
];

const steps = [
  {
    title: "A Fact Worth Keeping",
    desc: "The user says something that should survive future sessions.",
  },
  {
    title: "Stamp It After the Turn",
    desc: "Memory extraction happens after useful work, so the main loop stays focused.",
  },
  {
    title: "Write One Memory File",
    desc: "The durable detail goes into a Markdown file with a readable title and metadata.",
  },
  {
    title: "Update the Catalog",
    desc: "MEMORY.md is the cheap catalog: short enough to keep nearby.",
  },
  {
    title: "A Future Request Arrives",
    desc: "Later, the agent sees a new request and the catalog, not the whole library.",
  },
  {
    title: "Catalog Picks One",
    desc: "Selection chooses the one memory file that is relevant now.",
  },
  {
    title: "Build the Reading Stack",
    desc: "Only the selected memory joins the current request before the model call.",
  },
  {
    title: "Continuity Without Clutter",
    desc: "The answer reflects old context while unrelated memories stay on the shelf.",
  },
] as const;

const phases = ["learn", "catalog", "recall"] as const;

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const selectedFile = memoryFiles[0];
const unloadedFiles = memoryFiles.slice(1);
const catalogVisible = computed(() => currentStep.value >= 3);
const futureVisible = computed(() => currentStep.value >= 4);
const selected = computed(() => currentStep.value >= 5);
const injected = computed(() => currentStep.value >= 6);

function isPhaseActive(index: number) {
  if (index === 0) return currentStep.value <= 2;
  if (index === 1) return currentStep.value === 3 || selected.value;
  return futureVisible.value;
}

function surfaceClass(active: boolean) {
  return ["surface-card", { active }];
}

function typeClass(type: MemoryType) {
  if (type === "feedback") return "type-feedback";
  if (type === "project") return "type-project";
  return "type-reference";
}

const EmptyState = defineComponent({
  props: {
    label: { type: String, required: true },
  },
  setup(props) {
    return () => h("div", { class: "empty-state" }, props.label);
  },
});

const MemoryDetail = defineComponent({
  props: {
    file: { type: Object as () => MemoryFile, required: true },
    selected: { type: Boolean, required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: ["memory-detail", { selected: props.selected }] }, [
        h("div", { class: "detail-head" }, [
          h("div", { class: "detail-copy" }, [
            h("div", { class: "detail-title" }, props.file.title),
            h("div", { class: "mono detail-file" }, props.file.filename),
          ]),
          props.selected
            ? h("span", { class: "selected-pill" }, [h("span", { class: "check" }, "OK"), "selected"])
            : null,
        ]),
        h("div", { class: "detail-body" }, props.file.body),
      ]);
  },
});

const CatalogRow = defineComponent({
  props: {
    file: { type: Object as () => MemoryFile, required: true },
    visible: { type: Boolean, required: true },
    selected: { type: Boolean, required: true },
  },
  setup(props) {
    return () =>
      props.visible
        ? h("div", { class: ["catalog-row", { selected: props.selected }] }, [
            h("div", { class: "catalog-row-head" }, [
              h("div", { class: "catalog-title" }, props.file.title),
              h("span", { class: ["type-pill", typeClass(props.file.type)] }, props.file.type),
            ]),
            h("div", { class: "catalog-desc" }, props.file.description),
            h("div", { class: "mono catalog-file" }, props.file.filename),
          ])
        : null;
  },
});
</script>

<style scoped>
.memory-vis {
  min-height: 500px;
  color: #18181b;
}

.memory-vis h2 {
  margin: 0 0 16px;
  color: #18181b;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.memory-stage {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.phase-strip {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.phase-pill {
  border-radius: 8px;
  background: #f4f4f5;
  color: #71717a;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 650;
  text-transform: capitalize;
  transition:
    background 180ms ease,
    color 180ms ease;
}

.phase-pill.active {
  background: #ede9fe;
  color: #5b21b6;
}

.session-grid {
  display: grid;
  gap: 12px;
}

.surface-card {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  transition:
    background 180ms ease,
    border-color 180ms ease;
}

.surface-card.active {
  border-color: #c4b5fd;
  background: #f5f3ff;
}

.surface-head {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  color: #18181b;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.25;
}

.surface-head > span:last-child {
  min-width: 0;
  overflow-wrap: anywhere;
}

.surface-icon {
  display: inline-flex;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f4f4f5;
  color: #71717a;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
}

.surface-icon.active {
  background: #8b5cf6;
  color: #ffffff;
}

.surface-body,
.catalog-list,
.unloaded-list,
.stack-items {
  display: grid;
  gap: 12px;
}

.quote-card {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgb(24 24 27 / 0.05);
  color: #3f3f46;
  padding: 16px;
  font-size: 18px;
  line-height: 1.55;
}

.stamp-card,
.search-card {
  border: 1px solid #fde68a;
  border-radius: 8px;
  background: #fffbeb;
  color: #78350f;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.stamp-card div {
  margin-bottom: 4px;
  font-size: 16px;
  font-weight: 700;
}

.stamp-card p,
.unloaded-card p {
  margin: 0;
}

.search-card {
  border-color: #ddd6fe;
  background: #f5f3ff;
  color: #5b21b6;
}

.reading-stack {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.stack-title {
  margin-bottom: 12px;
  color: #18181b;
  font-size: 16px;
  font-weight: 700;
}

.stack-item {
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
}

.stack-item.current {
  background: #f4f4f5;
}

.stack-item.memory {
  background: #ede9fe;
  color: #5b21b6;
}

.stack-item.answer {
  background: #d1fae5;
  color: #065f46;
}

.library-card {
  margin-top: 12px;
}

.library-grid {
  display: grid;
  min-width: 0;
  gap: 12px;
}

.catalog-panel {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #fafafa;
  padding: 12px;
}

.catalog-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #27272a;
  font-size: 14px;
  font-weight: 700;
}

.catalog-head > span:first-child {
  border-radius: 6px;
  background: #e4e4e7;
  color: #52525b;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 800;
}

.catalog-row,
.unloaded-card,
.memory-detail {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
}

.catalog-row.selected,
.memory-detail.selected {
  border-color: #c4b5fd;
  background: #f5f3ff;
}

.catalog-row-head,
.unloaded-head,
.detail-head {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.catalog-title,
.unloaded-head > span:first-child,
.detail-title {
  min-width: 0;
  color: #18181b;
  font-size: 14px;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.catalog-desc,
.unloaded-card p {
  display: -webkit-box;
  margin-top: 6px;
  overflow: hidden;
  -webkit-box-orient: vertical;
  color: #71717a;
  font-size: 12px;
  line-height: 1.55;
  -webkit-line-clamp: 2;
}

.catalog-file,
.detail-file {
  margin-top: 8px;
  color: #71717a;
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-pill,
.selected-pill {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 4px;
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.2;
}

.type-feedback {
  background: #fef3c7;
  color: #92400e;
}

.type-project {
  background: #dbeafe;
  color: #1e40af;
}

.type-reference {
  background: #d1fae5;
  color: #065f46;
}

.selected-pill {
  background: #8b5cf6;
  color: #ffffff;
}

.check {
  font-size: 9px;
}

.detail-copy {
  min-width: 0;
}

.detail-title {
  font-size: 16px;
  overflow-wrap: anywhere;
  white-space: normal;
}

.detail-body {
  margin-top: 12px;
  border-radius: 8px;
  background: #ffffff;
  color: #3f3f46;
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.preview-title {
  margin-bottom: 12px;
  color: #71717a;
  font-size: 14px;
  font-weight: 700;
}

.preview-grid {
  display: grid;
  gap: 12px;
}

.empty-state {
  border: 1px dashed #d4d4d8;
  border-radius: 8px;
  color: #71717a;
  padding: 32px 16px;
  text-align: center;
  font-size: 14px;
}

.beginner-rule {
  margin: 16px 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #fafafa;
  color: #52525b;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.fade-up-enter-active,
.fade-up-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (min-width: 640px) {
  .phase-strip {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .library-grid {
    grid-template-columns: 320px minmax(0, 1fr);
  }

  .preview-grid {
    grid-template-columns: minmax(0, 1.15fr) minmax(220px, 0.85fr);
  }
}

@media (min-width: 1280px) {
  .session-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

:global(.dark) .memory-vis,
:global(.dark) .memory-vis h2,
:global(.dark) .surface-head,
:global(.dark) .stack-title,
:global(.dark) .catalog-title,
:global(.dark) .unloaded-head > span:first-child,
:global(.dark) .detail-title {
  color: #f4f4f5;
}

:global(.dark) .memory-stage,
:global(.dark) .surface-card,
:global(.dark) .quote-card,
:global(.dark) .reading-stack,
:global(.dark) .catalog-row,
:global(.dark) .unloaded-card,
:global(.dark) .memory-detail {
  border-color: #3f3f46;
  background: #18181b;
}

:global(.dark) .surface-card.active,
:global(.dark) .catalog-row.selected,
:global(.dark) .memory-detail.selected {
  border-color: #5b21b6;
  background: rgb(46 16 101 / 0.38);
}

:global(.dark) .phase-pill,
:global(.dark) .surface-icon,
:global(.dark) .stack-item.current,
:global(.dark) .catalog-head > span:first-child,
:global(.dark) .beginner-rule {
  background: #27272a;
  color: #d4d4d8;
}

:global(.dark) .phase-pill.active {
  background: rgb(91 33 182 / 0.35);
  color: #ddd6fe;
}

:global(.dark) .quote-card,
:global(.dark) .detail-body {
  color: #e4e4e7;
}

:global(.dark) .stamp-card {
  border-color: #78350f;
  background: rgb(69 26 3 / 0.45);
  color: #fde68a;
}

:global(.dark) .search-card {
  border-color: #5b21b6;
  background: rgb(46 16 101 / 0.45);
  color: #ddd6fe;
}

:global(.dark) .catalog-panel,
:global(.dark) .beginner-rule {
  border-color: #3f3f46;
}

:global(.dark) .catalog-panel {
  background: rgb(39 39 42 / 0.72);
}

:global(.dark) .catalog-desc,
:global(.dark) .unloaded-card p,
:global(.dark) .catalog-file,
:global(.dark) .detail-file,
:global(.dark) .preview-title,
:global(.dark) .empty-state {
  color: #a1a1aa;
}

:global(.dark) .empty-state {
  border-color: #3f3f46;
}
</style>
