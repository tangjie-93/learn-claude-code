<template>
  <section class="subagent-vis" data-testid="s06-subagent">
    <h2>{{ title || "Subagent Context Isolation" }}</h2>

    <div class="stage">
      <div class="process-grid">
        <article :class="['process-panel', 'parent-panel']">
          <div class="panel-head">
            <span class="status-dot parent-dot" />
            <span>Parent Process</span>
          </div>
          <div class="mono-label">messages[]</div>

          <TransitionGroup name="message" tag="div" class="message-list">
            <div v-for="message in parentMessages" :key="message.id" :class="messageClass(message)">
              {{ message.label }}
            </div>
          </TransitionGroup>

          <Transition name="fade">
            <div v-if="currentStep >= 5" class="context-note parent-note">
              3 original + 1 summary = clean context
            </div>
          </Transition>
        </article>

        <div class="isolation-wall" aria-label="Isolation boundary">
          <div class="wall-line" />
          <div :class="['wall-label', { active: currentStep >= 1 && currentStep <= 4 }]">ISOLATION</div>
          <div class="wall-line" />
        </div>

        <article :class="childPanelClass">
          <div class="panel-head">
            <span :class="['status-dot', childDotClass]" />
            <span>Child Process</span>
          </div>
          <div class="mono-label">messages[] (fresh)</div>

          <Transition name="fade">
            <div v-if="showChildEmpty" class="empty-child">not yet spawned</div>
          </Transition>

          <TransitionGroup name="message" tag="div" class="message-list">
            <div v-for="message in childMessages" :key="`${message.id}-child`" :class="messageClass(message, childFaded)">
              {{ message.label }}
            </div>
          </TransitionGroup>

          <Transition name="fade-scale">
            <div v-if="showCompression" class="context-note compression-note">
              Compressing full context into summary...
            </div>
          </Transition>

          <Transition name="fade">
            <div v-if="childDiscarded" class="context-note discard-note">context discarded</div>
          </Transition>
        </article>

        <Transition name="fly-task">
          <div v-if="showArcToChild" class="flying-label task-flight">task prompt</div>
        </Transition>

        <Transition name="fly-summary">
          <div v-if="showArcToParent" class="flying-label summary-flight">summary</div>
        </Transition>
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="current.title"
        :step-description="current.description"
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

interface MessageBlock {
  id: string;
  label: string;
  tone: "blue" | "zinc" | "emerald" | "purple" | "amber" | "teal";
}

const PARENT_BASE_MESSAGES: MessageBlock[] = [
  { id: "p1", label: "user: Build login + tests", tone: "blue" },
  { id: "p2", label: "assistant: Planning approach...", tone: "zinc" },
  { id: "p3", label: "tool_result: project structure", tone: "emerald" },
];

const TASK_PROMPT: MessageBlock = {
  id: "task",
  label: "task: Write unit tests for auth",
  tone: "purple",
};

const CHILD_WORK_MESSAGES: MessageBlock[] = [
  { id: "c1", label: "tool_use: read auth.ts", tone: "amber" },
  { id: "c2", label: "tool_use: write test.ts", tone: "amber" },
];

const SUMMARY_BLOCK: MessageBlock = {
  id: "summary",
  label: "summary: 3 tests written, all passing",
  tone: "teal",
};

const STEPS = [
  {
    title: "Parent Context",
    description: "The parent agent has accumulated messages from the conversation.",
  },
  {
    title: "Spawn Subagent",
    description: "Task tool creates a child with fresh messages[]. Only the task description is passed.",
  },
  {
    title: "Independent Work",
    description: "The child has its own context. It doesn't see the parent's history.",
  },
  {
    title: "Compress Result",
    description: "The child's full conversation compresses into one summary.",
  },
  {
    title: "Return Summary",
    description: "Only the summary returns. The child's full context is discarded.",
  },
  {
    title: "Clean Context",
    description: "The parent gets a clean summary without context bloat. This is fresh-context isolation via messages[].",
  },
] as const;

defineProps<{
  title?: string;
}>();

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEPS.length,
  autoPlayInterval: 2500,
});

const current = computed(() => STEPS[currentStep.value]);

const parentMessages = computed(() => {
  const base = [...PARENT_BASE_MESSAGES];
  if (currentStep.value >= 5) {
    base.push(SUMMARY_BLOCK);
  }
  return base;
});

const childMessages = computed(() => {
  if (currentStep.value < 1) return [];
  if (currentStep.value === 1) return [TASK_PROMPT];
  if (currentStep.value === 2) return [TASK_PROMPT, ...CHILD_WORK_MESSAGES];
  if (currentStep.value === 3) return [SUMMARY_BLOCK];
  return currentStep.value >= 4 ? [TASK_PROMPT, ...CHILD_WORK_MESSAGES] : [];
});

const showChildEmpty = computed(() => currentStep.value === 0);
const showArcToChild = computed(() => currentStep.value === 1);
const showCompression = computed(() => currentStep.value === 3);
const showArcToParent = computed(() => currentStep.value === 4);
const childDiscarded = computed(() => currentStep.value >= 4);
const childFaded = computed(() => currentStep.value >= 4);

const childPanelClass = computed(() => [
  "process-panel",
  "child-panel",
  {
    empty: showChildEmpty.value,
    discarded: childDiscarded.value,
    active: !showChildEmpty.value && !childDiscarded.value,
  },
]);

const childDotClass = computed(() => {
  if (showChildEmpty.value) return "empty-dot";
  if (childDiscarded.value) return "discarded-dot";
  return "child-dot";
});

function messageClass(message: MessageBlock, faded = false) {
  return ["message-block", `tone-${message.tone}`, { faded }];
}
</script>

<style scoped>
.subagent-vis {
  min-height: 500px;
}

.subagent-vis h2 {
  margin: 0 0 16px;
  color: #18181b;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.stage {
  min-height: 500px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.process-grid {
  position: relative;
  display: grid;
  min-height: 340px;
  grid-template-columns: minmax(0, 1fr) 36px minmax(0, 1fr);
  gap: 16px;
}

.process-panel {
  min-width: 0;
  border: 2px solid;
  border-radius: 12px;
  padding: 16px;
  transition:
    background-color 220ms ease,
    border-color 220ms ease,
    opacity 220ms ease;
}

.parent-panel {
  border-color: #93c5fd;
  background: rgba(239, 246, 255, 0.7);
}

.child-panel.empty {
  border-color: #d4d4d8;
  border-style: dashed;
  background: rgba(250, 250, 250, 0.75);
}

.child-panel.active {
  border-color: #c4b5fd;
  background: rgba(245, 243, 255, 0.72);
}

.child-panel.discarded {
  border-color: #d4d4d8;
  background: rgba(244, 244, 245, 0.72);
}

.panel-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #18181b;
  font-size: 14px;
  font-weight: 750;
}

.status-dot {
  width: 12px;
  height: 12px;
  flex: 0 0 auto;
  border-radius: 999px;
}

.parent-dot {
  background: #3b82f6;
}

.child-dot {
  background: #8b5cf6;
}

.empty-dot {
  background: #d4d4d8;
}

.discarded-dot {
  background: #a1a1aa;
}

.mono-label {
  margin-bottom: 8px;
  color: #71717a;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.message-list {
  display: grid;
  gap: 8px;
}

.message-block {
  min-width: 0;
  border-radius: 8px;
  padding: 8px 12px;
  color: #ffffff;
  font-size: 12px;
  font-weight: 650;
  line-height: 1.35;
  overflow-wrap: anywhere;
  box-shadow: 0 1px 2px rgba(24, 24, 27, 0.12);
  transition:
    opacity 220ms ease,
    transform 220ms ease;
}

.message-block.faded {
  opacity: 0.32;
}

.tone-blue {
  background: #3b82f6;
}

.tone-zinc {
  background: #52525b;
}

.tone-emerald {
  background: #10b981;
}

.tone-purple {
  background: #8b5cf6;
}

.tone-amber {
  background: #f59e0b;
}

.tone-teal {
  background: #14b8a6;
}

.empty-child {
  display: flex;
  min-height: 96px;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d4d4d8;
  border-radius: 8px;
  color: #71717a;
  font-size: 12px;
}

.context-note {
  margin-top: 12px;
  border: 1px solid;
  border-radius: 8px;
  padding: 6px 8px;
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.parent-note {
  border-color: #bfdbfe;
  background: rgba(255, 255, 255, 0.68);
  color: #2563eb;
}

.compression-note {
  border-color: #fcd34d;
  background: #fffbeb;
  color: #92400e;
}

.discard-note {
  border-color: #fecaca;
  background: #fef2f2;
  color: #dc2626;
}

.isolation-wall {
  display: flex;
  min-width: 0;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.wall-line {
  min-height: 72px;
  flex: 1 1 auto;
  border-left: 2px dashed #d4d4d8;
}

.wall-label {
  border-radius: 4px;
  background: #e4e4e7;
  padding: 6px 4px;
  color: #71717a;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  opacity: 0.48;
  text-orientation: mixed;
  writing-mode: vertical-rl;
  transition: opacity 220ms ease;
}

.wall-label.active {
  opacity: 1;
}

.flying-label {
  position: absolute;
  z-index: 2;
  top: 0;
  left: 0;
  border-radius: 8px;
  padding: 6px 12px;
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  pointer-events: none;
  box-shadow: 0 8px 20px rgba(24, 24, 27, 0.18);
}

.task-flight {
  background: #8b5cf6;
  transform: translate(55%, -10%);
}

.summary-flight {
  background: #14b8a6;
  transform: translate(15%, 200px);
}

.message-enter-active,
.message-leave-active,
.fade-enter-active,
.fade-leave-active,
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.message-enter-from,
.message-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.fade-enter-from,
.fade-leave-to,
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  transform: scale(0.96);
}

.fly-task-enter-active,
.fly-task-leave-active,
.fly-summary-enter-active,
.fly-summary-leave-active {
  transition:
    opacity 420ms ease,
    transform 720ms ease;
}

.fly-task-enter-from,
.fly-task-leave-to {
  opacity: 0;
  transform: translate(20%, -10%);
}

.fly-summary-enter-from,
.fly-summary-leave-to {
  opacity: 0;
  transform: translate(75%, 200px);
}

:deep(.step-controls) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
}

:deep(.step-copy strong) {
  display: block;
  color: #18181b;
  font-size: 14px;
  line-height: 1.35;
}

:deep(.step-copy p) {
  margin: 4px 0 0;
  color: #52525b;
  font-size: 13px;
  line-height: 1.45;
}

@media (max-width: 720px) {
  .process-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .isolation-wall {
    min-height: 42px;
    flex-direction: row;
  }

  .wall-line {
    width: 100%;
    min-height: 0;
    border-top: 2px dashed #d4d4d8;
    border-left: 0;
  }

  .wall-label {
    text-orientation: initial;
    writing-mode: horizontal-tb;
  }

  .flying-label {
    display: none;
  }
}
</style>
