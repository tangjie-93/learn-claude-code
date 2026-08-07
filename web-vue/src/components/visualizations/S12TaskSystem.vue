<template>
  <section class="task-system-vis" data-testid="s12-task-system">
    <h2>{{ title || "Task Board Dependencies" }}</h2>
    <div class="task-panel">
      <div class="board-head">
        <strong>.tasks board</strong>
        <div class="counts">
          <span>{{ lanes.blocked.length }} blocked</span>
          <span>{{ lanes.ready.length }} ready</span>
          <span>{{ lanes.active.length }} active</span>
          <span>{{ lanes.done.length }} done</span>
        </div>
      </div>

      <div class="lane-grid">
        <TaskLane title="Waiting" subtitle="blocked by another card" :tasks="lanes.blocked" />
        <TaskLane title="Ready" subtitle="can be claimed now" :tasks="lanes.ready" />
        <TaskLane title="Working" subtitle="currently in progress" :tasks="lanes.active" />
        <TaskLane title="Done" subtitle="unlocks dependents" :tasks="lanes.done" />
      </div>

      <div class="dependency-note">
        A dependency is a visible blocker badge on the card. Completion unlocks dependent work.
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
import { computed, defineComponent, h } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type Status = "blocked" | "ready" | "active" | "done";

interface TaskCard {
  id: string;
  title: string;
  blockers: string[];
  status: Status;
}

defineProps<{ title?: string }>();

const steps = [
  {
    title: "Tasks Become Files",
    desc: "The agent writes work as task cards on disk, so the plan survives compaction and restarts.",
  },
  {
    title: "Find the First Ready Card",
    desc: "A task with no blockers is ready immediately. Everything else waits visibly.",
  },
  {
    title: "Work One Card",
    desc: "The active task is not just text in the model's head; it has a durable status.",
  },
  {
    title: "Completion Unlocks Dependents",
    desc: "When T1 is done, the cards that depended on T1 become ready.",
  },
  {
    title: "Parallel Ready Work",
    desc: "T2 and T3 can run independently, while T4 still waits for both.",
  },
  {
    title: "All Blockers Cleared",
    desc: "Once T2 and T3 are done, T4 moves from waiting to active.",
  },
  {
    title: "Board Resolved",
    desc: "Every card reaches done. The dependency idea is visible without drawing a graph.",
  },
] as const;

const baseTasks = [
  { id: "T1", title: "Set up database", blockers: [] },
  { id: "T2", title: "Add API routes", blockers: ["T1"] },
  { id: "T3", title: "Build auth module", blockers: ["T1"] },
  { id: "T4", title: "Integration pass", blockers: ["T2", "T3"] },
  { id: "T5", title: "Deploy", blockers: ["T4"] },
];

const statusTable: Record<string, Status[]> = {
  T1: ["ready", "ready", "active", "done", "done", "done", "done"],
  T2: ["blocked", "blocked", "blocked", "ready", "active", "done", "done"],
  T3: ["blocked", "blocked", "blocked", "ready", "active", "done", "done"],
  T4: ["blocked", "blocked", "blocked", "blocked", "blocked", "active", "done"],
  T5: ["blocked", "blocked", "blocked", "blocked", "blocked", "blocked", "done"],
};

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const tasks = computed<TaskCard[]>(() =>
  baseTasks.map((task) => ({
    ...task,
    status: statusTable[task.id][currentStep.value] ?? "blocked",
  }))
);

const lanes = computed(() => ({
  blocked: tasks.value.filter((task) => task.status === "blocked"),
  ready: tasks.value.filter((task) => task.status === "ready"),
  active: tasks.value.filter((task) => task.status === "active"),
  done: tasks.value.filter((task) => task.status === "done"),
}));

const TaskLane = defineComponent({
  props: {
    title: { type: String, required: true },
    subtitle: { type: String, required: true },
    tasks: { type: Array as () => TaskCard[], required: true },
  },
  setup(props) {
    return () =>
      h("article", { class: "task-lane" }, [
        h("div", { class: "lane-head" }, [h("strong", props.title), h("span", props.subtitle)]),
        h(
          "div",
          { class: "lane-list" },
          props.tasks.length
            ? props.tasks.map((task) =>
                h("div", { class: ["task-card", task.status], "data-task": task.id, key: task.id }, [
                  h("div", { class: "task-top" }, [h("code", task.id), h("span", task.status)]),
                  h("strong", task.title),
                  h(
                    "div",
                    { class: "blocker-row" },
                    task.blockers.length
                      ? task.blockers.map((blocker) => h("small", { key: blocker }, `waits for ${blocker}`))
                      : [h("small", "no blockers")]
                  ),
                ])
              )
            : [h("div", { class: "empty-lane" }, "empty")]
        ),
      ]);
  },
});
</script>

<style scoped>
.task-system-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.task-system-vis h2 {
  margin: 0;
}

.task-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.board-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 12px;
}

.counts {
  display: grid;
  grid-template-columns: repeat(4, auto);
  gap: 8px;
  color: var(--text-muted);
  font-size: 12px;
}

.counts span {
  border-radius: 6px;
  background: var(--surface);
  padding: 5px 7px;
}

.lane-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.task-lane {
  display: grid;
  align-content: start;
  gap: 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
}

.lane-head {
  display: grid;
  gap: 3px;
}

.lane-head span {
  color: var(--text-muted);
  font-size: 11px;
}

.lane-list {
  display: grid;
  gap: 8px;
}

.task-card,
.empty-lane {
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 10px;
}

.task-card {
  display: grid;
  gap: 8px;
  box-shadow: 0 1px 8px rgba(15, 23, 42, 0.06);
}

.task-card.ready {
  border-color: #f59e0b;
  background: #fffbeb;
  color: #92400e;
}

.task-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.task-card.done {
  border-color: #10b981;
  background: #ecfdf5;
  color: #047857;
}

.task-card.blocked {
  opacity: 0.72;
}

.task-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 11px;
}

.task-top code,
.blocker-row small {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.task-card strong {
  font-size: 13px;
}

.blocker-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.blocker-row small {
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.7);
  padding: 3px 5px;
}

.empty-lane {
  border-style: dashed;
  color: var(--text-muted);
  text-align: center;
}

.dependency-note {
  border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--border));
  border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 9%, var(--surface));
  color: var(--text-muted);
  padding: 10px 12px;
  font-size: 12px;
}

@media (max-width: 900px) {
  .board-head {
    align-items: start;
    flex-direction: column;
  }

  .counts,
  .lane-grid {
    grid-template-columns: 1fr;
  }
}
</style>
