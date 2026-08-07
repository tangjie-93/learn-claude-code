<template>
  <section class="todo-write-vis" data-testid="s05-todo-write">
    <h2>{{ title || "TodoWrite Nag System" }}</h2>

    <div class="board-panel">
      <div class="nag-area">
        <div class="nag-head">
          <span>Nag Timer</span>
          <span class="mono">{{ nagValue }}/{{ NAG_THRESHOLD }}</span>
        </div>
        <div class="nag-track" :class="{ firing: nagFires }">
          <div class="nag-fill" :class="nagTone" :style="{ width: `${nagPct}%` }" />
        </div>

        <Transition name="nag-message">
          <div v-if="nagFires" data-testid="system-nag" class="system-nag">
            SYSTEM: "You have pending tasks. Pick one up now!"
          </div>
        </Transition>
      </div>

      <div class="kanban-grid">
        <KanbanColumn title="Pending" :tasks="pendingTasks" tone="pending" />
        <KanbanColumn title="In Progress" :tasks="inProgressTasks" tone="active" />
        <KanbanColumn title="Completed" :tasks="completedTasks" tone="complete" />
      </div>

      <div class="progress-summary">
        <span class="mono">Progress: {{ completedTasks.length }}/{{ tasks.length }} complete</span>
        <div class="progress-blocks" aria-label="Task completion summary">
          <span
            v-for="task in tasks"
            :key="task.id"
            :class="['progress-block', `status-${task.status}`]"
          />
        </div>
      </div>
    </div>

    <StepControls
      :current-step="currentStep"
      :total-steps="totalSteps"
      :is-playing="isPlaying"
      :step-title="stepInfo.title"
      :step-description="stepInfo.desc"
      @prev="prev"
      @next="next"
      @reset="reset"
      @toggle="toggleAutoPlay"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, TransitionGroup } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type TaskStatus = "pending" | "in_progress" | "completed";
type ColumnTone = "pending" | "active" | "complete";

interface Task {
  id: number;
  label: string;
  status: TaskStatus;
}

defineProps<{
  title?: string;
}>();

const TASK_STATES: Task[][] = [
  [
    { id: 1, label: "Write auth tests", status: "pending" },
    { id: 2, label: "Fix mobile layout", status: "pending" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "pending" },
    { id: 2, label: "Fix mobile layout", status: "pending" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "pending" },
    { id: 2, label: "Fix mobile layout", status: "pending" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "in_progress" },
    { id: 2, label: "Fix mobile layout", status: "pending" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "completed" },
    { id: 2, label: "Fix mobile layout", status: "pending" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "completed" },
    { id: 2, label: "Fix mobile layout", status: "in_progress" },
    { id: 3, label: "Add error handling", status: "pending" },
    { id: 4, label: "Update config loader", status: "pending" },
  ],
  [
    { id: 1, label: "Write auth tests", status: "completed" },
    { id: 2, label: "Fix mobile layout", status: "completed" },
    { id: 3, label: "Add error handling", status: "completed" },
    { id: 4, label: "Update config loader", status: "in_progress" },
  ],
];

const NAG_TIMER_PER_STEP = [0, 1, 2, 3, 0, 0, 0] as const;
const NAG_FIRES_PER_STEP = [false, false, false, true, false, false, false] as const;
const NAG_THRESHOLD = 3;

const STEP_INFO = [
  { title: "The Plan", desc: "TodoWrite gives the model a visible plan. All tasks start as pending." },
  { title: "Round 1 - Idle", desc: "The model does work but does not touch its todos. The nag counter increments." },
  { title: "Round 2 - Still Idle", desc: "Two rounds without progress. Pressure builds." },
  { title: "NAG!", desc: 'Threshold reached. System message injected: "You have pending tasks. Pick one up now!"' },
  { title: "Task Complete", desc: "The model completes the task. Working on todos resets the timer to 0." },
  { title: "Self-Directed", desc: "Once the model learns the pattern, it picks up tasks voluntarily." },
  { title: "Mission Accomplished", desc: "Visible plan plus nag pressure produces reliable task completion." },
] as const;

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: TASK_STATES.length,
  autoPlayInterval: 2500,
});

const tasks = computed(() => TASK_STATES[currentStep.value]);
const nagValue = computed(() => NAG_TIMER_PER_STEP[currentStep.value]);
const nagFires = computed(() => NAG_FIRES_PER_STEP[currentStep.value]);
const stepInfo = computed(() => STEP_INFO[currentStep.value]);
const pendingTasks = computed(() => tasks.value.filter((task) => task.status === "pending"));
const inProgressTasks = computed(() => tasks.value.filter((task) => task.status === "in_progress"));
const completedTasks = computed(() => tasks.value.filter((task) => task.status === "completed"));
const nagPct = computed(() => Math.min((nagValue.value / NAG_THRESHOLD) * 100, 100));
const nagTone = computed(() => {
  if (nagValue.value === 0) return "tone-idle";
  if (nagValue.value === 1) return "tone-low";
  if (nagValue.value === 2) return "tone-warn";
  return "tone-fire";
});

function taskCardClass(status: TaskStatus) {
  return ["task-card", `status-${status}`];
}

function statusLabel(status: TaskStatus) {
  return status.replace("_", " ");
}

const TaskCard = defineComponent({
  props: {
    task: { type: Object as () => Task, required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: taskCardClass(props.task.status) }, [
        h("div", { class: "task-meta" }, [
          h("span", { class: "mono task-id" }, `#${props.task.id}`),
          h("span", { class: "status-pill" }, statusLabel(props.task.status)),
        ]),
        h("div", { class: "task-label" }, props.task.label),
      ]);
  },
});

const KanbanColumn = defineComponent({
  props: {
    title: { type: String, required: true },
    tasks: { type: Array as () => Task[], required: true },
    tone: { type: String as () => ColumnTone, required: true },
  },
  setup(props) {
    return () =>
      h("article", { class: ["kanban-column", `column-${props.tone}`], "data-testid": "kanban-column" }, [
        h("div", { class: "column-head" }, [
          h("span", { class: "column-title" }, props.title),
          h("span", { class: "column-count" }, props.tasks.length),
        ]),
        h(
          TransitionGroup,
          { name: "task-move", tag: "div", class: "task-list" },
          {
            default: () =>
              props.tasks.length > 0
                ? props.tasks.map((task) => h(TaskCard, { key: task.id, task }))
                : [h("div", { key: "empty", class: "empty-column" }, "--")],
          },
        ),
      ]);
  },
});
</script>

<style scoped>
.todo-write-vis {
  min-height: 500px;
  color: #18181b;
}

.todo-write-vis h2 {
  margin: 0 0 16px;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.board-panel {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.nag-area {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
}

.nag-head,
.progress-summary,
.task-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.nag-head {
  color: #52525b;
  font-size: 12px;
  font-weight: 650;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.nag-track {
  position: relative;
  height: 16px;
  overflow: hidden;
  border-radius: 999px;
  background: #e4e4e7;
}

.nag-track.firing {
  outline: 2px solid #ef4444;
  outline-offset: 1px;
}

.nag-fill {
  height: 100%;
  border-radius: inherit;
  transition:
    width 420ms ease,
    background-color 180ms ease;
}

.tone-idle {
  background: #d4d4d8;
}

.tone-low {
  background: #4ade80;
}

.tone-warn {
  background: #facc15;
}

.tone-fire {
  background: #ef4444;
}

.system-nag {
  border: 1px solid #fca5a5;
  border-radius: 8px;
  background: #fef2f2;
  padding: 10px 12px;
  color: #991b1b;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.35;
  text-align: center;
}

.kanban-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
}

.kanban-column {
  min-width: 0;
  min-height: 220px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #fafafa;
}

.column-head {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 38px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.2;
  text-align: center;
  text-transform: uppercase;
}

.column-title {
  min-width: 0;
  overflow-wrap: anywhere;
}

.column-count {
  display: inline-flex;
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  font-size: 10px;
  font-weight: 800;
}

.column-pending .column-head {
  background: #e4e4e7;
  color: #3f3f46;
}

.column-active .column-head {
  background: #fef3c7;
  color: #92400e;
}

.column-complete .column-head {
  background: #d1fae5;
  color: #065f46;
}

.task-list {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
}

.task-card {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 10px;
  box-shadow: 0 1px 2px rgba(24, 24, 27, 0.08);
  transition:
    opacity 180ms ease,
    transform 180ms ease,
    background-color 180ms ease,
    border-color 180ms ease;
}

.task-card.status-pending {
  border-color: #e4e4e7;
}

.task-card.status-in_progress {
  border-color: #fcd34d;
  background: #fffbeb;
}

.task-card.status-completed {
  border-color: #a7f3d0;
  background: #ecfdf5;
}

.task-id {
  color: #a1a1aa;
  font-size: 10px;
}

.status-pill {
  flex: 0 0 auto;
  border-radius: 999px;
  background: #f4f4f5;
  padding: 3px 6px;
  color: #52525b;
  font-size: 9px;
  font-weight: 750;
  line-height: 1.1;
  text-transform: uppercase;
}

.status-in_progress .status-pill {
  background: #fef3c7;
  color: #92400e;
}

.status-completed .status-pill {
  background: #d1fae5;
  color: #065f46;
}

.task-label {
  margin-top: 6px;
  color: #3f3f46;
  font-size: 12px;
  font-weight: 650;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.empty-column {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  color: #a1a1aa;
  font-size: 12px;
}

.progress-summary {
  margin-top: 12px;
  border-radius: 8px;
  background: #f4f4f5;
  padding: 10px 12px;
  color: #71717a;
  font-size: 11px;
}

.progress-blocks {
  display: flex;
  flex: 0 0 auto;
  gap: 3px;
}

.progress-block {
  width: 24px;
  height: 8px;
  border-radius: 3px;
  background: #d4d4d8;
}

.progress-block.status-in_progress {
  background: #f59e0b;
}

.progress-block.status-completed {
  background: #10b981;
}

.nag-message-enter-active,
.nag-message-leave-active,
.task-move-enter-active,
.task-move-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.nag-message-enter-from,
.nag-message-leave-to,
.task-move-enter-from,
.task-move-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

:deep(.step-controls) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
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

:deep(.step-actions) {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

:deep(.step-buttons) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.step-buttons button) {
  min-height: 32px;
  border: 1px solid #d4d4d8;
  border-radius: 6px;
  background: #ffffff;
  padding: 0 12px;
  color: #27272a;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

:deep(.step-buttons button:disabled) {
  cursor: not-allowed;
  opacity: 0.45;
}

:deep(.step-progress) {
  display: flex;
  align-items: center;
  gap: 5px;
}

:deep(.step-progress span) {
  width: 18px;
  height: 6px;
  border-radius: 999px;
  background: #e4e4e7;
}

:deep(.step-progress span.done) {
  background: #a7f3d0;
}

:deep(.step-progress span.active) {
  background: #ef4444;
}

:deep(.step-progress em) {
  margin-left: 6px;
  color: #71717a;
  font-size: 12px;
  font-style: normal;
}

@media (min-width: 640px) {
  .kanban-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .kanban-column {
    min-height: 280px;
  }
}
</style>
