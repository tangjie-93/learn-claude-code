<template>
  <section class="agent-teams-vis" data-testid="s15-agent-teams">
    <h2>{{ title || "Agent Team Mailboxes" }}</h2>

    <div class="team-stage">
      <div class="team-grid">
        <article v-for="agent in agents" :key="agent.id" :class="['agent-panel', agentState(agent.id)]">
          <div class="agent-head">
            <div>
              <strong>{{ agent.label }}</strong>
              <p>{{ agent.role }}</p>
            </div>
            <span class="state-badge">{{ agentState(agent.id) }}</span>
          </div>

          <div class="inbox-panel">
            <div class="inbox-head">
              <span aria-hidden="true">IN</span>
              <strong>{{ agent.id }}.jsonl</strong>
            </div>

            <TransitionGroup name="mail-list" tag="div" class="inbox-stack">
              <MailCard v-for="mail in visibleMail(agent.id)" :key="mail.id" :mail="mail" />
              <div v-if="visibleMail(agent.id).length === 0" key="empty" class="empty-inbox">inbox empty</div>
            </TransitionGroup>
          </div>
        </article>

        <aside class="activity-log">
          <div class="activity-head">
            <span aria-hidden="true">TM</span>
            <strong>What changed</strong>
          </div>

          <TransitionGroup name="activity-list" tag="div" class="activity-list">
            <div v-for="item in activityItems" :key="item" class="activity-item">{{ item }}</div>
          </TransitionGroup>
        </aside>
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
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type AgentId = "lead" | "coder" | "reviewer";
type AgentState = "waiting" | "reading" | "working" | "reviewing" | "done";

interface Mail {
  id: string;
  from: AgentId;
  to: AgentId;
  subject: string;
  body: string;
  appearsAt: number;
  consumedAt?: number;
}

defineProps<{
  title?: string;
}>();

const agents: { id: AgentId; label: string; role: string }[] = [
  { id: "lead", label: "Lead", role: "splits work and reads results" },
  { id: "coder", label: "Coder", role: "implements one slice" },
  { id: "reviewer", label: "Reviewer", role: "checks the result" },
];

const mail: Mail[] = [
  {
    id: "assign",
    from: "lead",
    to: "coder",
    subject: "Build login UI",
    body: "Please implement the login form and report back.",
    appearsAt: 1,
    consumedAt: 2,
  },
  {
    id: "result",
    from: "coder",
    to: "reviewer",
    subject: "Login UI done",
    body: "Files changed, ready for review.",
    appearsAt: 4,
    consumedAt: 5,
  },
  {
    id: "feedback",
    from: "reviewer",
    to: "lead",
    subject: "Review passed",
    body: "No blockers. One small polish note.",
    appearsAt: 5,
  },
];

const steps = [
  {
    title: "A Team Is Mailboxes",
    desc: "Each agent has its own inbox file. The team does not need shared memory to coordinate.",
  },
  {
    title: "Lead Drops a Card",
    desc: "Assigning work means appending a message to the coder's inbox.",
  },
  {
    title: "Coder Reads Before Thinking",
    desc: "Before its next model call, the coder drains its inbox and turns messages into context.",
  },
  {
    title: "Coder Works Alone",
    desc: "The coder now runs its own loop. The lead does not have to hold the full context.",
  },
  {
    title: "Result Becomes Mail",
    desc: "The coder sends a result card to the reviewer through the same mailbox mechanism.",
  },
  {
    title: "Reviewer Sends Feedback",
    desc: "Review feedback is just another card. The lead reads it from its inbox.",
  },
  {
    title: "Files Are the Coordination Layer",
    desc: "The whole team is inspectable as append-only inbox files: lead.jsonl, coder.jsonl, reviewer.jsonl.",
  },
] as const;

const logItems = [
  "team config creates lead, coder, reviewer",
  "lead appends task card to coder.jsonl",
  "coder drains inbox before model call",
  "coder works in its own loop",
  "coder appends result to reviewer.jsonl",
  "reviewer appends feedback to lead.jsonl",
  "all coordination remains visible on disk",
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const activityItems = computed(() => logItems.slice(0, currentStep.value + 1));

function visibleMail(agent: AgentId) {
  return mail.filter(
    (item) =>
      item.to === agent &&
      item.appearsAt <= currentStep.value &&
      (item.consumedAt === undefined || currentStep.value < item.consumedAt)
  );
}

function agentState(agent: AgentId): AgentState {
  const step = currentStep.value;
  if (agent === "lead" && step === 1) return "working";
  if (agent === "coder" && step === 2) return "reading";
  if (agent === "coder" && (step === 3 || step === 4)) return "working";
  if (agent === "reviewer" && step === 5) return "reviewing";
  if (agent === "lead" && step >= 5) return "reading";
  if (step === 6) return "done";
  return "waiting";
}

const MailCard = defineComponent({
  props: {
    mail: { type: Object as () => Mail, required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: "mail-card", "data-mail": props.mail.id }, [
        h("div", { class: "mail-route" }, [
          h("span", `${props.mail.from} -> ${props.mail.to}`),
          h("span", { "aria-hidden": "true" }, "MSG"),
        ]),
        h("strong", props.mail.subject),
        h("p", props.mail.body),
      ]);
  },
});
</script>

<style scoped>
.agent-teams-vis {
  display: grid;
  min-height: 500px;
  gap: 16px;
}

.agent-teams-vis h2 {
  margin: 0;
}

.team-stage {
  display: grid;
  gap: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(220px, 0.9fr);
  gap: 12px;
}

.agent-panel,
.activity-log {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
}

.agent-panel {
  display: grid;
  align-content: start;
  gap: 12px;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.agent-panel.waiting {
  border-color: var(--border);
  background: var(--surface);
}

.agent-panel.working {
  border-color: #60a5fa;
  background: #eff6ff;
}

.agent-panel.reading,
.agent-panel.reviewing {
  border-color: #f59e0b;
  background: #fffbeb;
}

.agent-panel.done {
  border-color: #10b981;
  background: #ecfdf5;
}

.agent-head {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 10px;
}

.agent-head strong {
  color: var(--text);
  font-size: 16px;
}

.agent-head p,
.mail-card p {
  margin: 0;
}

.agent-head p {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.5;
}

.state-badge {
  flex: 0 0 auto;
  border-radius: 6px;
  background: var(--surface);
  box-shadow: 0 1px 6px rgba(15, 23, 42, 0.08);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  padding: 5px 8px;
  text-transform: capitalize;
}

.inbox-panel {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  padding: 12px;
}

.inbox-head,
.activity-head {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text);
  font-size: 14px;
}

.inbox-head span,
.activity-head span {
  border-radius: 5px;
  background: color-mix(in srgb, var(--accent) 12%, var(--surface));
  color: var(--accent);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 10px;
  font-weight: 800;
  padding: 3px 5px;
}

.inbox-stack {
  display: grid;
  min-height: 118px;
  gap: 8px;
  margin-top: 10px;
}

.mail-card {
  display: grid;
  gap: 6px;
  border: 1px solid #fcd34d;
  border-radius: 7px;
  background: #fffbeb;
  box-shadow: 0 1px 8px rgba(146, 64, 14, 0.08);
  color: #92400e;
  padding: 10px;
}

.mail-route {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  font-weight: 700;
}

.mail-card strong {
  font-size: 14px;
  line-height: 1.35;
}

.mail-card p {
  font-size: 12px;
  line-height: 1.5;
  opacity: 0.86;
}

.empty-inbox {
  display: grid;
  min-height: 96px;
  place-items: center;
  border: 1px dashed var(--border);
  border-radius: 7px;
  color: var(--text-muted);
  font-size: 12px;
}

.activity-log {
  display: grid;
  align-content: start;
  gap: 10px;
  background: var(--surface-soft);
}

.activity-list {
  display: grid;
  gap: 8px;
}

.activity-item {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  color: var(--text);
  font-size: 12px;
  line-height: 1.45;
  padding: 9px 10px;
}

.mail-list-enter-active,
.mail-list-leave-active,
.activity-list-enter-active,
.activity-list-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.mail-list-enter-from,
.activity-list-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}

.mail-list-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}

.activity-list-leave-to {
  opacity: 0;
  transform: translateX(8px);
}

@media (max-width: 1100px) {
  .team-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .team-grid {
    grid-template-columns: 1fr;
  }
}
</style>
