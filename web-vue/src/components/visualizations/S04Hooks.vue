<template>
  <section class="hooks-vis" data-testid="s04-hooks">
    <h2>{{ title || "Hook Workbench" }}</h2>
    <div class="hooks-panel">
      <div class="hooks-note">
        The loop stays boring on purpose: it calls <code>trigger_hooks(event)</code>, and the registry decides
        what extra logic runs.
      </div>

      <div class="hooks-grid">
        <article class="hook-surface">
          <h3>Hook registry</h3>
          <div class="hook-cards">
            <div
              v-for="hook in hooks"
              :key="hook.id"
              :data-hook="hook.id"
              :class="['hook-card', hook.tone, { active: activeHook === hook.id }]"
            >
              <div class="hook-head">
                <strong>{{ hook.id }}</strong>
                <span v-if="activeHook === hook.id">active</span>
              </div>
              <p>{{ hook.when }}</p>
              <div class="callback-row">
                <code v-for="callback in hook.callbacks" :key="callback">{{ callback }}</code>
              </div>
            </div>
          </div>
        </article>

        <article class="hook-surface">
          <h3>This turn</h3>
          <div class="turn-card">
            <strong>{{ turnState.title }}</strong>
            <code>{{ turnState.body }}</code>
          </div>
          <div class="audit-log">
            <h4>Audit log</h4>
            <code v-for="item in auditItems" :key="item">{{ item }}</code>
          </div>
        </article>
      </div>

      <div class="hooks-note muted">
        Beginner rule: adding behavior means registering a callback, not editing the core model-tool-result loop.
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="current.title"
        :step-description="current.desc"
        @reset="reset"
        @prev="prev"
        @toggle="toggleAutoPlay"
        @next="next"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

defineProps<{ title?: string }>();

const hooks = [
  { id: "UserPromptSubmit", when: "after input, before LLM", callbacks: ["context_inject_hook"], tone: "blue" },
  { id: "PreToolUse", when: "after tool_use, before handler", callbacks: ["permission_hook", "log_hook"], tone: "amber" },
  { id: "PostToolUse", when: "after handler, before next turn", callbacks: ["large_output_hook"], tone: "emerald" },
  { id: "Stop", when: "before final output", callbacks: ["summary_hook"], tone: "zinc" },
] as const;

const steps = [
  {
    title: "Hooks Are Registered Outside the Loop",
    desc: "The loop only knows event names; callback behavior lives in the registry.",
    active: null,
  },
  {
    title: "UserPromptSubmit",
    desc: "Input hooks can log, validate, or inject context before the model sees the prompt.",
    active: "UserPromptSubmit",
  },
  {
    title: "The Core Loop Still Chooses a Tool",
    desc: "Calling the model and receiving function_call remains the same as before.",
    active: null,
  },
  {
    title: "PreToolUse",
    desc: "Permission and logging hooks run before the handler touches the workspace.",
    active: "PreToolUse",
  },
  {
    title: "PostToolUse",
    desc: "Result hooks inspect output or trigger side effects after execution.",
    active: "PostToolUse",
  },
  {
    title: "Stop",
    desc: "Cleanup and summary hooks run when the model stops asking for tools.",
    active: "Stop",
  },
] as const;

const turnStates = [
  { title: "User input", body: "Read README.md and summarize it." },
  { title: "User input", body: "UserPromptSubmit hooks inspect the prompt." },
  { title: "LLM chooses tool", body: "function_call: read_file({ path: 'README.md' })" },
  { title: "Tool waits at pre-hook", body: "permission_hook + log_hook inspect the call." },
  { title: "Handler returned output", body: "large_output_hook checks result size." },
  { title: "No more function_call", body: "summary_hook records final session stats." },
];

const auditLog = [
  "[registry] four hook slots registered",
  "[UserPromptSubmit] working directory logged",
  "[loop] model returned read_file function_call",
  "[PreToolUse] permission allowed; tool call logged",
  "[PostToolUse] output size checked",
  "[Stop] session used 1 tool call",
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const activeHook = computed(() => current.value.active);
const turnState = computed(() => turnStates[currentStep.value]);
const auditItems = computed(() => auditLog.slice(0, currentStep.value + 1));
</script>

<style scoped>
.hooks-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.hooks-vis h2,
.hook-surface h3,
.audit-log h4 {
  margin: 0;
}

.hooks-panel,
.hook-surface,
.audit-log {
  display: grid;
  gap: 14px;
}

.hooks-panel,
.hook-surface {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.hooks-note {
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  background: #ecfdf5;
  color: #065f46;
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.55;
}

:root.dark .hooks-note {
  border-color: #064e3b;
  background: rgba(6, 78, 59, 0.34);
  color: #a7f3d0;
}

.hooks-note.muted {
  border-color: var(--border);
  background: var(--surface-soft);
  color: var(--text-muted);
}

.hooks-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 14px;
}

.hook-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.hook-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.hook-card.active {
  transform: translateY(-2px);
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 10%, var(--surface));
}

.hook-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.hook-head strong,
.callback-row code,
.turn-card code,
.audit-log code,
.hooks-note code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.hook-head strong {
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 13px;
}

.hook-head span {
  border-radius: 999px;
  background: var(--accent);
  color: white;
  padding: 2px 7px;
  font-size: 11px;
}

.hook-card p {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.45;
}

.callback-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.callback-row code,
.audit-log code {
  border-radius: 6px;
  background: var(--surface-soft);
  color: var(--text);
  padding: 5px 7px;
  font-size: 11px;
}

.turn-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 14px;
}

.turn-card code {
  white-space: normal;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.55;
}

.audit-log code {
  display: block;
}

@media (max-width: 900px) {
  .hooks-grid,
  .hook-cards {
    grid-template-columns: 1fr;
  }
}
</style>
