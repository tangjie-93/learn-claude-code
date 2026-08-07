<template>
  <section class="worktree-vis" data-testid="s18-worktree-isolation">
    <h2>{{ title || "Worktree Task Isolation" }}</h2>
    <div class="worktree-panel">
      <pre class="operation">{{ step.op }}</pre>
      <div class="worktree-grid">
        <article class="worktree-column">
          <h3>Task Board</h3>
          <div class="row-list">
            <div v-for="task in step.tasks" :key="task.id" :class="['task-row', task.status]">
              <div class="row-head">
                <code>#{{ task.id }}</code>
                <span>{{ task.status }}</span>
              </div>
              <strong>{{ task.subject }}</strong>
              <small>worktree: {{ task.worktree || "-" }}</small>
            </div>
          </div>
        </article>

        <article class="worktree-column">
          <h3>Worktree Index</h3>
          <div class="row-list">
            <div v-if="!step.worktrees.length" class="empty-row">no worktrees yet</div>
            <div
              v-for="worktree in step.worktrees"
              :key="worktree.name"
              :data-worktree="worktree.name"
              :class="['worktree-row', worktree.state]"
            >
              <strong>{{ worktree.name }}</strong>
              <code>{{ worktree.branch }}</code>
              <small>task: {{ worktree.task }}</small>
            </div>
          </div>
        </article>

        <article class="worktree-column">
          <h3>Execution Lanes</h3>
          <div class="row-list">
            <div
              v-for="lane in step.lanes"
              :key="lane.name"
              :data-lane="lane.name"
              :class="['lane-row', { highlight: lane.highlight }]"
            >
              <strong>{{ lane.name }}</strong>
              <code v-if="!lane.files.length">(no changes)</code>
              <code v-for="file in lane.files" v-else :key="file">{{ file }}</code>
            </div>
          </div>
        </article>
      </div>

      <div class="step-summary">
        <strong>{{ step.title }}</strong>
        <p>{{ step.desc }}</p>
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="step.title"
        :step-description="step.desc"
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

type TaskStatus = "pending" | "in_progress" | "completed";

interface TaskRow {
  id: number;
  subject: string;
  status: TaskStatus;
  worktree: string;
}

interface WorktreeRow {
  name: string;
  branch: string;
  task: string;
  state: "active" | "kept" | "removed";
}

interface Lane {
  name: string;
  files: string[];
  highlight?: boolean;
}

interface StepState {
  title: string;
  desc: string;
  op: string;
  tasks: TaskRow[];
  worktrees: WorktreeRow[];
  lanes: Lane[];
}

defineProps<{ title?: string }>();

const steps: StepState[] = [
  {
    title: "Single Workspace Pain",
    desc: "Two tasks are active, but both edits would hit one directory and collide.",
    op: "task_create x2",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "in_progress", worktree: "" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "" },
    ],
    worktrees: [],
    lanes: [
      { name: "main", files: ["auth/service.py", "ui/Login.tsx"], highlight: true },
      { name: "wt/auth-refactor", files: [] },
      { name: "wt/ui-login", files: [] },
    ],
  },
  {
    title: "Allocate Lane for Task 1",
    desc: "Create a worktree lane and associate it with task 1 for clear ownership.",
    op: "worktree_create(name='auth-refactor', task_id=1)",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "in_progress", worktree: "auth-refactor" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "" },
    ],
    worktrees: [{ name: "auth-refactor", branch: "wt/auth-refactor", task: "#1", state: "active" }],
    lanes: [
      { name: "main", files: ["ui/Login.tsx"] },
      { name: "wt/auth-refactor", files: ["auth/service.py"], highlight: true },
      { name: "wt/ui-login", files: [] },
    ],
  },
  {
    title: "Allocate Lane for Task 2",
    desc: "Lane creation and task association can be separate. Task 2 binds after lane creation.",
    op: "worktree_create(name='ui-login')\ntask_bind_worktree(task_id=2, worktree='ui-login')",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "in_progress", worktree: "auth-refactor" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "ui-login" },
    ],
    worktrees: [
      { name: "auth-refactor", branch: "wt/auth-refactor", task: "#1", state: "active" },
      { name: "ui-login", branch: "wt/ui-login", task: "#2", state: "active" },
    ],
    lanes: [
      { name: "main", files: [] },
      { name: "wt/auth-refactor", files: ["auth/service.py"] },
      { name: "wt/ui-login", files: ["ui/Login.tsx"], highlight: true },
    ],
  },
  {
    title: "Run Commands in Isolated Lanes",
    desc: "Each command routes by selected lane directory, not by the shared root.",
    op: "worktree_run('auth-refactor', 'pytest tests/auth -q')",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "in_progress", worktree: "auth-refactor" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "ui-login" },
    ],
    worktrees: [
      { name: "auth-refactor", branch: "wt/auth-refactor", task: "#1", state: "active" },
      { name: "ui-login", branch: "wt/ui-login", task: "#2", state: "active" },
    ],
    lanes: [
      { name: "main", files: [] },
      { name: "wt/auth-refactor", files: ["auth/service.py", "tests/auth/test_login.py"], highlight: true },
      { name: "wt/ui-login", files: ["ui/Login.tsx", "ui/Login.css"] },
    ],
  },
  {
    title: "Keep One Lane, Close Another",
    desc: "Closeout can mix decisions: keep one lane, remove another, complete its task.",
    op: "worktree_keep('ui-login')\nworktree_remove('auth-refactor', complete_task=true)",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "completed", worktree: "" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "ui-login" },
    ],
    worktrees: [
      { name: "auth-refactor", branch: "wt/auth-refactor", task: "#1", state: "removed" },
      { name: "ui-login", branch: "wt/ui-login", task: "#2", state: "kept" },
    ],
    lanes: [
      { name: "main", files: [] },
      { name: "wt/auth-refactor", files: [] },
      { name: "wt/ui-login", files: ["ui/Login.tsx"], highlight: true },
    ],
  },
  {
    title: "Isolation + Coordination + Events",
    desc: "The board tracks shared truth, lanes isolate execution, and events create audit traces.",
    op: "task_list + worktree_list + worktree_events",
    tasks: [
      { id: 1, subject: "Auth refactor", status: "completed", worktree: "" },
      { id: 2, subject: "UI login polish", status: "in_progress", worktree: "ui-login" },
    ],
    worktrees: [
      { name: "auth-refactor", branch: "wt/auth-refactor", task: "#1", state: "removed" },
      { name: "ui-login", branch: "wt/ui-login", task: "#2", state: "kept" },
    ],
    lanes: [
      { name: "main", files: [] },
      { name: "wt/auth-refactor", files: [] },
      { name: "wt/ui-login", files: ["ui/Login.tsx"], highlight: true },
    ],
  },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2600,
});

const step = computed(() => steps[currentStep.value]);
</script>

<style scoped>
.worktree-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.worktree-vis h2,
.worktree-column h3 {
  margin: 0;
}

.worktree-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.operation {
  margin: 0;
  border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--border));
  border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 8%, var(--surface));
  color: var(--accent);
  padding: 10px;
  white-space: pre-wrap;
}

.worktree-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.worktree-column {
  display: grid;
  align-content: start;
  gap: 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
}

.row-list {
  display: grid;
  gap: 8px;
}

.task-row,
.worktree-row,
.lane-row,
.empty-row {
  display: grid;
  gap: 6px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  padding: 10px;
}

.row-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.row-head span {
  border-radius: 999px;
  background: var(--surface-soft);
  color: var(--text-muted);
  padding: 2px 7px;
  font-size: 11px;
}

.worktree-row.active,
.lane-row.highlight {
  border-color: #3b82f6;
  background: #eff6ff;
}

.worktree-row.kept {
  border-color: #0ea5e9;
  background: #f0f9ff;
}

.worktree-row.removed {
  opacity: 0.65;
}

.task-row.completed {
  border-color: #10b981;
  background: #ecfdf5;
}

.task-row.in_progress {
  border-color: #f59e0b;
  background: #fffbeb;
}

.task-row code,
.worktree-row code,
.lane-row code,
.task-row small,
.worktree-row small {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  color: var(--text-muted);
  font-size: 11px;
}

.empty-row {
  border-style: dashed;
  color: var(--text-muted);
  text-align: center;
}

.step-summary {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 12px;
}

.step-summary p {
  margin: 4px 0 0;
  color: var(--text-muted);
  line-height: 1.55;
}

@media (max-width: 900px) {
  .worktree-grid {
    grid-template-columns: 1fr;
  }
}
</style>
