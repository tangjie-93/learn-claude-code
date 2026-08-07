<template>
  <section class="autonomous-vis" data-testid="s17-autonomous-agents">
    <h2>{{ title || "Autonomous Work Board" }}</h2>
    <div class="auto-panel">
      <div class="auto-grid">
        <article class="agent-column">
          <h3>Agents watch their own idle timer</h3>
          <div class="agent-list">
            <div v-for="agent in agents" :key="agent.id" :data-agent="agent.id" :class="['agent-card', agent.phase]">
              <div class="agent-head">
                <strong>Agent {{ agent.id }}</strong>
                <span>{{ agent.phase }}</span>
              </div>
              <div class="timer-track">
                <div class="timer-fill" :style="{ width: `${Math.round(agent.timer * 100)}%` }" />
              </div>
              <code>{{ agent.task ? `task: ${agent.task}` : `idle timer: ${Math.round(agent.timer * 100)}%` }}</code>
            </div>
          </div>
        </article>

        <article class="board-column">
          <h3>Shared task board</h3>
          <div class="task-grid">
            <div v-for="task in tasks" :key="task.id" :data-task="task.id" :class="['board-task', task.status]">
              <div class="task-head">
                <code>{{ task.id }}</code>
                <span>{{ task.status }}</span>
              </div>
              <strong>{{ task.title }}</strong>
              <small>owner: {{ task.owner || "-" }}</small>
            </div>
          </div>
          <p>Nobody assigns tasks directly; agents claim visible open cards when their timers wake them.</p>
        </article>
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

type AgentPhase = "idle" | "polling" | "claiming" | "working" | "done";
type TaskStatus = "open" | "claimed" | "complete";

interface AgentState {
  id: string;
  phase: AgentPhase;
  timer: number;
  task?: string;
}

defineProps<{ title?: string }>();

const steps = [
  { title: "Quiet Agents", desc: "Autonomous agents start by waiting. The work board matters more than a central dispatcher." },
  { title: "Idle Timer Fills", desc: "An agent watches its idle timer. When it waits long enough, it looks for work." },
  { title: "Read the Board", desc: "The agent polls the shared task board and looks for an open card." },
  { title: "Claim One Card", desc: "Claiming writes the agent name onto one task, making ownership visible." },
  { title: "Work Independently", desc: "The claimed task moves into the agent workspace. No coordinator babysits it." },
  { title: "Others Join In", desc: "A second agent can claim a different card through the same habit." },
  { title: "Finish and Free Up", desc: "Completed work goes back to the board as done, and the agent returns to waiting." },
  { title: "Self Organization", desc: "Timers plus visible ownership let a small group organize itself without a manager loop." },
] as const;

const taskBase = [
  { id: "T1", title: "Fix auth bug" },
  { id: "T2", title: "Add rate limiter" },
  { id: "T3", title: "Write docs" },
  { id: "T4", title: "Clean tests" },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const agents = computed<AgentState[]>(() => {
  const step = currentStep.value;
  if (step === 0) return [{ id: "A", phase: "idle", timer: 0.1 }, { id: "B", phase: "idle", timer: 0 }, { id: "C", phase: "idle", timer: 0 }];
  if (step === 1) return [{ id: "A", phase: "idle", timer: 0.85 }, { id: "B", phase: "idle", timer: 0.25 }, { id: "C", phase: "idle", timer: 0 }];
  if (step === 2) return [{ id: "A", phase: "polling", timer: 1 }, { id: "B", phase: "idle", timer: 0.25 }, { id: "C", phase: "idle", timer: 0 }];
  if (step === 3) return [{ id: "A", phase: "claiming", timer: 0, task: "T1" }, { id: "B", phase: "idle", timer: 0.45 }, { id: "C", phase: "idle", timer: 0.1 }];
  if (step === 4) return [{ id: "A", phase: "working", timer: 0, task: "T1" }, { id: "B", phase: "idle", timer: 0.65 }, { id: "C", phase: "idle", timer: 0.2 }];
  if (step === 5) return [{ id: "A", phase: "working", timer: 0, task: "T1" }, { id: "B", phase: "claiming", timer: 0, task: "T2" }, { id: "C", phase: "idle", timer: 0.35 }];
  if (step === 6) return [{ id: "A", phase: "done", timer: 0, task: "T1" }, { id: "B", phase: "working", timer: 0, task: "T2" }, { id: "C", phase: "idle", timer: 0.6 }];
  return [{ id: "A", phase: "idle", timer: 0.15 }, { id: "B", phase: "working", timer: 0, task: "T2" }, { id: "C", phase: "claiming", timer: 0, task: "T3" }];
});

const tasks = computed(() =>
  taskBase.map((task) => {
    const step = currentStep.value;
    let status: TaskStatus = "open";
    let owner = "";
    if (task.id === "T1" && step >= 6) {
      status = "complete";
      owner = "A";
    } else if (task.id === "T1" && step >= 3) {
      status = "claimed";
      owner = "A";
    } else if (task.id === "T2" && step >= 5) {
      status = "claimed";
      owner = "B";
    } else if (task.id === "T3" && step >= 7) {
      status = "claimed";
      owner = "C";
    }
    return { ...task, status, owner };
  })
);
</script>

<style scoped>
.autonomous-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.autonomous-vis h2,
.agent-column h3,
.board-column h3 {
  margin: 0;
}

.auto-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.auto-grid {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 14px;
}

.agent-column,
.board-column {
  display: grid;
  align-content: start;
  gap: 12px;
}

.agent-list,
.task-grid {
  display: grid;
  gap: 10px;
}

.task-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.agent-card,
.board-task {
  display: grid;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.agent-card.polling,
.agent-card.claiming,
.board-task.claimed {
  border-color: #f59e0b;
  background: #fffbeb;
}

.agent-card.working {
  border-color: #10b981;
  background: #ecfdf5;
}

.agent-card.done,
.board-task.complete {
  border-color: #3b82f6;
  background: #eff6ff;
}

.agent-head,
.task-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.agent-head span,
.task-head span {
  border-radius: 999px;
  background: var(--surface-soft);
  color: var(--text-muted);
  padding: 2px 7px;
  font-size: 11px;
  text-transform: capitalize;
}

.timer-track {
  overflow: hidden;
  height: 8px;
  border-radius: 999px;
  background: var(--surface-soft);
}

.timer-fill {
  height: 100%;
  border-radius: inherit;
  background: #f59e0b;
  transition: width 0.25s ease;
}

.agent-card code,
.task-head code,
.board-task small {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.agent-card code,
.board-task small,
.board-column p {
  color: var(--text-muted);
  font-size: 12px;
}

.board-column p {
  margin: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 10px;
  line-height: 1.55;
}

@media (max-width: 900px) {
  .auto-grid,
  .task-grid {
    grid-template-columns: 1fr;
  }
}
</style>
