<template>
  <section class="cron-scheduler-vis" data-testid="s14-cron-scheduler">
    <h2>{{ title || "Cron Scheduler" }}</h2>

    <div class="scheduler-shell">
      <div class="weekly-clock">
        <div class="clock-head">
          <div class="clock-title">
            <span class="mini-icon">Cal</span>
            <strong>Weekly clock</strong>
          </div>
          <div class="time-chip" :class="{ pulsing: currentStep >= 2 && currentStep <= 4 }">
            {{ currentStep < 2 ? "08:59" : "09:00" }}
          </div>
        </div>

        <div class="day-grid">
          <div
            v-for="(day, index) in days"
            :key="day"
            class="day-cell"
            :class="{ 'active-day': currentStep >= 2 && index === 2 }"
            :data-day="day"
          >
            {{ day }}
          </div>
        </div>
      </div>

      <div class="flow-grid">
        <section class="flow-panel" :class="{ active: scheduleBookActive }">
          <div class="panel-head">
            <span class="panel-icon">DB</span>
            <strong>Schedule book</strong>
          </div>

          <div class="panel-stack">
            <div v-if="currentStep === 0" class="schedule-card blue">
              <code>Draft prompt</code>
              <span>review open PR every weekday</span>
            </div>

            <div v-if="currentStep >= 1" class="schedule-card" :class="currentStep === 5 ? 'green' : 'blue'">
              <code>0 9 * * 1-5</code>
              <span>review open PR every weekday</span>
            </div>

            <div class="empty-note">
              {{ currentStep >= 1 ? "stored schedules stay here" : "no saved schedule yet" }}
            </div>
          </div>
        </section>

        <section class="flow-panel" :class="{ active: dueQueueActive }">
          <div class="panel-head">
            <span class="panel-icon">CLK</span>
            <strong>Due queue</strong>
          </div>

          <div class="panel-stack">
            <div class="watcher-row">watcher: {{ currentStep >= 2 ? "running" : "waiting" }}</div>

            <div v-if="currentStep >= 3 && currentStep <= 4" class="schedule-card amber">
              <code>due copy</code>
              <span>same prompt, current timestamp</span>
            </div>

            <div v-if="currentStep < 3" class="empty-note tall">queue is empty</div>

            <div v-if="currentStep === 5" class="schedule-card green">
              <code>queue drained</code>
              <span>ready for next tick</span>
            </div>
          </div>
        </section>

        <section class="flow-panel" :class="{ active: agentInboxActive }">
          <div class="panel-head">
            <span class="panel-icon">IN</span>
            <strong>Agent inbox</strong>
          </div>

          <div class="panel-stack">
            <div v-if="currentStep >= 4" class="schedule-card" :class="currentStep >= 5 ? 'green' : 'blue'">
              <code>agent turn</code>
              <span>{{ currentStep >= 5 ? "result appended" : "runs like a normal prompt" }}</span>
            </div>

            <div class="agent-status">
              <span class="status-mark">{{ currentStep >= 5 ? "OK" : "AI" }}</span>
              <span>{{ currentStep >= 5 ? "review summary saved" : "agent loop available" }}</span>
            </div>
          </div>
        </section>
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

type ActiveArea = "composer" | "ledger" | "clock" | "queue" | "inbox" | "done";

defineProps<{ title?: string }>();

const steps = [
  {
    title: "Make It Repeatable",
    desc: "The user turns one normal prompt into a reusable schedule card.",
    active: "composer",
  },
  {
    title: "Store the Card",
    desc: "The schedule lives in durable data, so it is not tied to the current chat turn.",
    active: "ledger",
  },
  {
    title: "Time Keeps Moving",
    desc: "A tiny scheduler watches the clock while the agent can do other work.",
    active: "clock",
  },
  {
    title: "Copy Goes to the Queue",
    desc: "When the cron expression matches, the scheduler puts a due copy in the queue.",
    active: "queue",
  },
  {
    title: "Run as a Normal Turn",
    desc: "The queue processor hands the due prompt to the same agent loop beginners already know.",
    active: "inbox",
  },
  {
    title: "Keep the Original",
    desc: "The result is recorded, and the schedule card remains ready for the next matching time.",
    active: "done",
  },
] as const satisfies readonly { title: string; desc: string; active: ActiveArea }[];

const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const scheduleBookActive = computed(() => ["ledger", "done"].includes(current.value.active));
const dueQueueActive = computed(() => ["clock", "queue"].includes(current.value.active));
const agentInboxActive = computed(() => ["inbox", "done"].includes(current.value.active));
</script>

<style scoped>
.cron-scheduler-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.cron-scheduler-vis h2 {
  margin: 0;
}

.scheduler-shell {
  display: grid;
  gap: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.weekly-clock {
  display: grid;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 12px;
}

.clock-head,
.panel-head,
.clock-title,
.agent-status {
  display: flex;
  align-items: center;
}

.clock-head {
  justify-content: space-between;
  gap: 12px;
}

.clock-title,
.panel-head,
.agent-status {
  gap: 8px;
}

.mini-icon,
.panel-icon,
.status-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0;
}

.mini-icon {
  width: 30px;
  height: 26px;
  background: #eef2ff;
  color: #3730a3;
}

.time-chip {
  border-radius: 6px;
  background: var(--surface);
  box-shadow: 0 1px 6px rgba(15, 23, 42, 0.08);
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  padding: 6px 8px;
}

.time-chip.pulsing {
  animation: clock-pulse 1.1s ease-in-out infinite;
}

.day-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.day-cell {
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 9px 6px;
  text-align: center;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease;
}

.day-cell.active-day {
  border-color: #f59e0b;
  background: #fef3c7;
  color: #92400e;
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.flow-panel {
  min-height: 230px;
  display: grid;
  align-content: start;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.flow-panel.active {
  border-color: #93c5fd;
  background: #eff6ff;
}

.panel-head {
  color: var(--text);
  font-size: 14px;
}

.panel-icon {
  width: 28px;
  height: 28px;
  background: var(--surface-soft);
  color: var(--text-muted);
}

.flow-panel.active .panel-icon {
  background: #2563eb;
  color: #fff;
}

.panel-stack {
  display: grid;
  gap: 12px;
}

.schedule-card,
.empty-note,
.watcher-row,
.agent-status {
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 10px;
}

.schedule-card {
  display: grid;
  gap: 5px;
  box-shadow: 0 1px 8px rgba(15, 23, 42, 0.06);
  animation: card-enter 180ms ease-out;
}

.schedule-card code {
  font-size: 12px;
  font-weight: 700;
}

.schedule-card span,
.watcher-row,
.agent-status,
.empty-note {
  font-size: 12px;
}

.schedule-card span {
  opacity: 0.82;
}

.schedule-card.blue {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.schedule-card.amber {
  border-color: #fcd34d;
  background: #fffbeb;
  color: #92400e;
}

.schedule-card.green {
  border-color: #6ee7b7;
  background: #ecfdf5;
  color: #047857;
}

.empty-note {
  border-style: dashed;
  color: var(--text-muted);
  text-align: center;
}

.empty-note.tall {
  padding-block: 30px;
}

.watcher-row,
.agent-status {
  background: var(--surface-soft);
  color: var(--text-muted);
}

.status-mark {
  width: 24px;
  height: 24px;
  background: var(--surface);
  color: var(--text-muted);
}

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes clock-pulse {
  50% {
    transform: scale(1.06);
  }
}

@media (max-width: 820px) {
  .flow-grid {
    grid-template-columns: 1fr;
  }

  .flow-panel {
    min-height: 0;
  }
}

@media (max-width: 520px) {
  .scheduler-shell {
    padding: 12px;
  }

  .clock-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .day-grid {
    gap: 6px;
  }
}
</style>
