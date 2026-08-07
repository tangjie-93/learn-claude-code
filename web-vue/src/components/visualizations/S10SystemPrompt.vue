<template>
  <section class="system-prompt-vis" data-testid="s10-system-prompt">
    <h2>{{ title || "Runtime Prompt Assembly" }}</h2>

    <div class="stage">
      <div class="assembly-grid">
        <article :class="surfaceClass(sourceActive)">
          <div class="surface-head">
            <span class="surface-icon">CTX</span>
            <span>Runtime context</span>
          </div>

          <div class="source-grid">
            <div
              v-for="source in SOURCES"
              :key="source.id"
              :class="['source-card', `tone-${source.tone}`, { active: sourceActive }]"
            >
              <div class="card-label">
                <span class="mini-icon">{{ source.icon }}</span>
                <span>{{ source.label }}</span>
              </div>
              <code>{{ source.value }}</code>
            </div>
          </div>
        </article>

        <article :class="surfaceClass(sectionsSurfaceActive)">
          <div class="surface-head">
            <span class="surface-icon">SEC</span>
            <span>Section shelf + cache</span>
          </div>

          <div class="section-stack">
            <div class="section-grid">
              <div
                v-for="section in SECTIONS"
                :key="section.id"
                :class="['section-card', { active: sectionsActive || promptActive }]"
              >
                <div class="section-top">
                  <span>{{ section.title }}</span>
                  <span v-if="sectionsActive || promptActive" class="check-mark" aria-label="selected">OK</span>
                </div>
                <div class="owner">owner: {{ section.owner }}</div>
                <p>{{ section.body }}</p>
              </div>
            </div>

            <div :class="['cache-panel', cacheToneClass]">
              <div class="card-label">
                <span class="mini-icon">KEY</span>
                <span>context key</span>
              </div>
              <code>json.dumps(context, sort_keys=True)</code>
              <div class="cache-state">{{ cacheStateText }}</div>
            </div>
          </div>
        </article>

        <article :class="surfaceClass(promptActive)">
          <div class="surface-head">
            <span class="surface-icon">LLM</span>
            <span>System prompt</span>
          </div>

          <Transition name="fade" mode="out-in">
            <div v-if="!promptActive" key="empty" class="empty-prompt">prompt not built yet</div>
            <div v-else key="preview" class="prompt-preview">
              <div v-for="section in SECTIONS" :key="`prompt-${section.id}`" class="prompt-section">
                <div class="prompt-title">[{{ section.title }}]</div>
                <p>{{ section.body }}</p>
              </div>
              <div :class="['prompt-status', { llm: mode === 'llm' }]">
                <div class="status-title">
                  <span class="mini-icon">RUN</span>
                  <span>{{ mode === "llm" ? "sent to LLM" : "system prompt ready" }}</span>
                </div>
                <p>Traceable prompt text, assembled from named runtime owners.</p>
              </div>
            </div>
          </Transition>
        </article>
      </div>

      <p class="beginner-rule">
        Beginner rule: system prompts should be assembled from named runtime facts, then cached only when those facts are
        unchanged.
      </p>

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
import { computed } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type StepMode = (typeof STEPS)[number]["mode"];

interface SourceItem {
  id: string;
  label: string;
  value: string;
  icon: string;
  tone: "blue" | "emerald" | "amber" | "violet";
}

interface PromptSection {
  id: string;
  title: string;
  body: string;
  owner: string;
}

defineProps<{
  title?: string;
}>();

const STEPS = [
  {
    title: "Runtime State Arrives",
    desc: "The prompt is not a fixed paragraph; it starts from workspace, tools, memory, and skills.",
    mode: "state",
  },
  {
    title: "Section Shelf Selects Owners",
    desc: "Each subsystem owns one prompt section, so a bad rule has a place to debug.",
    mode: "sections",
  },
  {
    title: "Context Key Checks the Cache",
    desc: "The same runtime state produces the same deterministic cache key.",
    mode: "cache-miss",
  },
  {
    title: "Prompt Is Assembled",
    desc: "Selected sections are joined into one system prompt that the LLM can read.",
    mode: "assemble",
  },
  {
    title: "Same Key Reuses the Prompt",
    desc: "If nothing changed, the runtime skips assembly and reuses the cached prompt.",
    mode: "cache-hit",
  },
  {
    title: "LLM Sees the Built Prompt",
    desc: "The model receives a traceable product of runtime state, not a stale hardcoded string.",
    mode: "llm",
  },
] as const;

const SOURCES: SourceItem[] = [
  { id: "workspace", label: "workspace", value: "/repo", icon: "BOX", tone: "blue" },
  { id: "tools", label: "tools", value: "bash, read_file", icon: "TOOL", tone: "emerald" },
  { id: "memory", label: "memory", value: "enabled", icon: "MEM", tone: "amber" },
  { id: "skills", label: "skills", value: "code-review", icon: "LIB", tone: "violet" },
];

const SECTIONS: PromptSection[] = [
  { id: "identity", title: "identity", body: "You are a helpful coding agent.", owner: "core" },
  { id: "tools", title: "tools", body: "Available tools: bash, read_file.", owner: "tool registry" },
  { id: "workspace", title: "workspace", body: "Current workspace: /repo.", owner: "runtime" },
  { id: "memory", title: "memory + skills", body: "Load memory index and code-review skill.", owner: "context loader" },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEPS.length,
  autoPlayInterval: 2600,
});

const current = computed(() => STEPS[currentStep.value]);
const mode = computed<StepMode>(() => current.value.mode);
const sourceActive = computed(() => mode.value === "state" || mode.value === "sections" || mode.value === "cache-miss");
const sectionsActive = computed(() => mode.value === "sections" || mode.value === "assemble");
const promptActive = computed(() => mode.value === "assemble" || mode.value === "cache-hit" || mode.value === "llm");
const sectionsSurfaceActive = computed(() => sectionsActive.value || mode.value === "cache-miss" || mode.value === "cache-hit");

const cacheStateText = computed(() => {
  if (mode.value === "cache-hit") return "cache hit: reuse prompt";
  if (mode.value === "cache-miss") return "cache miss: assemble sections";
  return "waiting for state";
});

const cacheToneClass = computed(() => ({
  active: mode.value === "cache-miss" || mode.value === "cache-hit",
  hit: mode.value === "cache-hit",
}));

function surfaceClass(active: boolean) {
  return ["surface", { active }];
}
</script>

<style scoped>
.system-prompt-vis {
  min-height: 500px;
  color: #18181b;
}

.system-prompt-vis h2 {
  margin: 0 0 16px;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.stage {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.assembly-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.1fr) minmax(0, 0.95fr);
  gap: 12px;
}

.surface {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.surface.active {
  border-color: #93c5fd;
  background: #eff6ff;
}

.surface-head {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  color: #18181b;
  font-size: 18px;
  font-weight: 650;
  line-height: 1.25;
}

.surface-icon {
  display: inline-flex;
  width: 40px;
  height: 40px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f4f4f5;
  color: #52525b;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 11px;
  font-weight: 700;
}

.surface.active .surface-icon {
  background: #3b82f6;
  color: #ffffff;
}

.source-grid,
.section-grid {
  display: grid;
  gap: 8px;
}

.source-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.section-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.source-card,
.section-card,
.cache-panel,
.prompt-section,
.prompt-status {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
}

.source-card {
  padding: 12px;
  color: #3f3f46;
}

.source-card.active.tone-blue {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.source-card.active.tone-emerald {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #047857;
}

.source-card.active.tone-amber {
  border-color: #fde68a;
  background: #fffbeb;
  color: #92400e;
}

.source-card.active.tone-violet {
  border-color: #ddd6fe;
  background: #f5f3ff;
  color: #6d28d9;
}

.card-label,
.status-title {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 650;
}

.mini-icon {
  flex: 0 0 auto;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 11px;
  font-weight: 700;
}

code {
  display: block;
  min-width: 0;
  overflow-wrap: anywhere;
  border-radius: 6px;
  background: rgb(255 255 255 / 0.72);
  padding: 6px 8px;
  color: inherit;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.section-stack {
  display: grid;
  gap: 12px;
}

.section-card {
  padding: 12px;
}

.section-card.active {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #065f46;
}

.section-top {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.35;
}

.check-mark {
  flex: 0 0 auto;
  border-radius: 999px;
  background: #10b981;
  padding: 1px 6px;
  color: #ffffff;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 10px;
}

.owner {
  margin-bottom: 8px;
  color: #71717a;
  font-size: 12px;
  line-height: 1.35;
}

.section-card p,
.prompt-section p,
.prompt-status p,
.beginner-rule {
  margin: 0;
  color: #3f3f46;
  font-size: 14px;
  line-height: 1.55;
}

.cache-panel {
  padding: 12px;
  color: #52525b;
}

.cache-panel.active {
  border-color: #fde68a;
  background: #fffbeb;
  color: #92400e;
}

.cache-panel.active.hit {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #047857;
}

.cache-state {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.4;
}

.empty-prompt {
  border: 1px dashed #d4d4d8;
  border-radius: 8px;
  padding: 32px 16px;
  color: #71717a;
  font-size: 14px;
  line-height: 1.4;
  text-align: center;
}

.prompt-preview {
  display: grid;
  gap: 8px;
}

.prompt-section {
  padding: 12px;
}

.prompt-title {
  margin-bottom: 4px;
  color: #1d4ed8;
  font-family:
    ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.35;
}

.prompt-status {
  border-color: #e4e4e7;
  background: #f4f4f5;
  padding: 16px;
}

.prompt-status.llm {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.beginner-rule {
  margin-top: 12px;
  margin-bottom: 16px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #f4f4f5;
  padding: 12px 16px;
  color: #52525b;
}

.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 160ms ease,
    transform 160ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@media (max-width: 1100px) {
  .assembly-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stage,
  .surface {
    padding: 12px;
  }

  .source-grid,
  .section-grid {
    grid-template-columns: 1fr;
  }

  .surface-head {
    font-size: 16px;
  }
}

:global(.dark) .system-prompt-vis {
  color: #f4f4f5;
}

:global(.dark) .system-prompt-vis h2,
:global(.dark) .surface-head {
  color: #f4f4f5;
}

:global(.dark) .stage,
:global(.dark) .surface,
:global(.dark) .source-card,
:global(.dark) .section-card,
:global(.dark) .cache-panel,
:global(.dark) .prompt-section {
  border-color: #3f3f46;
  background: #18181b;
}

:global(.dark) .surface.active,
:global(.dark) .prompt-status.llm {
  border-color: #1e3a8a;
  background: rgb(30 58 138 / 0.35);
}

:global(.dark) .surface-icon {
  background: #27272a;
  color: #d4d4d8;
}

:global(.dark) .source-card.active.tone-blue {
  border-color: #1e3a8a;
  background: rgb(30 58 138 / 0.35);
  color: #bfdbfe;
}

:global(.dark) .source-card.active.tone-emerald,
:global(.dark) .section-card.active,
:global(.dark) .cache-panel.active.hit {
  border-color: #064e3b;
  background: rgb(6 78 59 / 0.35);
  color: #a7f3d0;
}

:global(.dark) .source-card.active.tone-amber,
:global(.dark) .cache-panel.active {
  border-color: #78350f;
  background: rgb(120 53 15 / 0.35);
  color: #fde68a;
}

:global(.dark) .source-card.active.tone-violet {
  border-color: #4c1d95;
  background: rgb(76 29 149 / 0.35);
  color: #ddd6fe;
}

:global(.dark) .owner,
:global(.dark) .empty-prompt,
:global(.dark) .beginner-rule {
  color: #a1a1aa;
}

:global(.dark) .section-card p,
:global(.dark) .prompt-section p,
:global(.dark) .prompt-status p {
  color: #e4e4e7;
}

:global(.dark) code {
  background: rgb(9 9 11 / 0.45);
}

:global(.dark) .empty-prompt {
  border-color: #3f3f46;
}

:global(.dark) .prompt-status,
:global(.dark) .beginner-rule {
  border-color: #3f3f46;
  background: rgb(39 39 42 / 0.72);
}
</style>
