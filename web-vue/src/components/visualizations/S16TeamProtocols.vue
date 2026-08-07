<template>
  <section class="team-protocols-vis" data-testid="s16-team-protocols">
    <h2>{{ title || "Team Protocol Cards" }}</h2>

    <div class="protocol-panel">
      <div class="protocol-toggle" aria-label="Protocol mode">
        <button
          type="button"
          data-protocol="shutdown"
          :class="{ active: protocol === 'shutdown' }"
          @click="switchProtocol('shutdown')"
        >
          Shutdown
        </button>
        <button
          type="button"
          data-protocol="plan"
          :class="{ active: protocol === 'plan' }"
          @click="switchProtocol('plan')"
        >
          Plan Approval
        </button>
      </div>

      <div class="state-rail">
        <div class="state-head">
          <strong>Protocol state</strong>
          <code>request_id: {{ requestId }}</code>
        </div>
        <div class="state-list">
          <template v-for="(state, index) in protocolStates" :key="state.label">
            <div class="state-card" :class="{ active: index === currentStep, done: index < currentStep }">
              <strong>{{ state.label }}</strong>
              <span>{{ state.detail }}</span>
            </div>
            <span v-if="index < protocolStates.length - 1" class="state-arrow" aria-hidden="true">-&gt;</span>
          </template>
        </div>
      </div>

      <div class="desk-grid">
        <article class="desk" :class="{ active: leaderActive }">
          <div class="desk-head">
            <span class="desk-icon" aria-hidden="true">L</span>
            <strong>Leader desk</strong>
          </div>
          <div class="tray">
            <TransitionGroup name="card-list">
              <div
                v-if="!isPlan && currentStep >= 1"
                key="shutdown-request"
                class="protocol-card"
                :class="currentStep >= 3 ? 'tone-zinc' : 'tone-blue'"
              >
                <strong>shutdown_request</strong>
                <code>request_id: {{ requestId }}</code>
                <code>target: teammate</code>
                <code>mode: polite</code>
              </div>
              <div
                v-if="!isPlan && currentStep >= 3"
                key="shutdown-response"
                class="protocol-card tone-emerald"
              >
                <strong>shutdown_response</strong>
                <code>request_id: {{ requestId }}</code>
                <code>approve: true</code>
                <code>status: closed</code>
              </div>
              <div
                v-if="isPlan && currentStep >= 2"
                key="plan-approved"
                class="protocol-card tone-emerald"
              >
                <strong>plan_approval_response</strong>
                <code>request_id: {{ requestId }}</code>
                <code>approve: true</code>
                <code>unlock: implementation</code>
              </div>
            </TransitionGroup>
            <div v-if="(!isPlan && currentStep === 0) || (isPlan && currentStep < 2)" class="empty-tray">
              waiting for a protocol card
            </div>
          </div>
        </article>

        <article class="desk" :class="{ active: sharedActive }">
          <div class="desk-head">
            <span class="desk-icon" aria-hidden="true">S</span>
            <strong>Shared card shape</strong>
          </div>
          <div class="tray">
            <div class="protocol-card tone-amber">
              <strong>protocol fields</strong>
              <code>type</code>
              <code>request_id</code>
              <code>payload</code>
              <code>response</code>
            </div>
            <div class="protocol-note">The key idea is correlation, not ceremony.</div>
            <div v-if="isPlan" class="lock-note">
              <span aria-hidden="true">LOCK</span>
              implementation locked until approval
            </div>
          </div>
        </article>

        <article class="desk" :class="{ active: teammateActive }">
          <div class="desk-head">
            <span class="desk-icon" aria-hidden="true">T</span>
            <strong>Teammate desk</strong>
          </div>
          <div class="tray">
            <TransitionGroup name="card-list">
              <div
                v-if="!isPlan && currentStep >= 2"
                key="teammate-decision"
                class="protocol-card"
                :class="currentStep >= 3 ? 'tone-emerald' : 'tone-amber'"
              >
                <strong>decision card</strong>
                <code>request_id: {{ requestId }}</code>
                <code>choice: approve</code>
                <code>state: {{ currentStep >= 3 ? "exited" : "deciding" }}</code>
              </div>
              <div
                v-if="isPlan && currentStep >= 1"
                key="plan-card"
                class="protocol-card"
                :class="currentStep >= 2 ? 'tone-emerald' : 'tone-blue'"
              >
                <strong>exit_plan_mode</strong>
                <code>request_id: {{ requestId }}</code>
                <code>1. edit module</code>
                <code>2. run tests</code>
                <code>3. report diff</code>
              </div>
            </TransitionGroup>
            <div v-if="(!isPlan && currentStep < 2) || (isPlan && currentStep === 0)" class="empty-tray">
              {{ isPlan ? "draft plan not submitted" : "no request received" }}
            </div>
          </div>
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
import { computed, ref } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type Protocol = "shutdown" | "plan";

interface ProtocolStep {
  title: string;
  desc: string;
}

interface ProtocolState {
  label: string;
  detail: string;
}

defineProps<{ title?: string }>();

const requestId = "req_abc";

const shutdownSteps: ProtocolStep[] = [
  {
    title: "Agree on a Small Form",
    desc: "A protocol is just a shared card shape: request type, request_id, and the expected answer.",
  },
  {
    title: "Leader Files a Request",
    desc: "The leader writes a shutdown request card instead of force-stopping the teammate.",
  },
  {
    title: "Teammate Chooses",
    desc: "The teammate can approve or reject, and the request_id keeps the answer attached to the right request.",
  },
  {
    title: "Clean Exit",
    desc: "The approved response returns to the leader, and the teammate exits cleanly.",
  },
];

const planSteps: ProtocolStep[] = [
  {
    title: "Work Is Locked",
    desc: "In plan mode, implementation stays locked until a plan card is approved.",
  },
  {
    title: "Submit the Plan Card",
    desc: "The teammate sends a concrete plan with the same request-response shape.",
  },
  {
    title: "Approval Unlocks Action",
    desc: "The leader approves the card, then implementation can begin.",
  },
];

const protocolStateTable: Record<Protocol, ProtocolState[]> = {
  shutdown: [
    { label: "drafted", detail: "Lead creates request_id" },
    { label: "pending", detail: "card waits in inbox" },
    { label: "deciding", detail: "teammate replies" },
    { label: "closed", detail: "Lead matches response" },
  ],
  plan: [
    { label: "locked", detail: "work cannot start" },
    { label: "submitted", detail: "plan card is sent" },
    { label: "approved", detail: "implementation unlocks" },
  ],
};

const protocol = ref<Protocol>("shutdown");
const steps = computed(() => (protocol.value === "shutdown" ? shutdownSteps : planSteps));
const protocolStates = computed(() => protocolStateTable[protocol.value]);

const shutdownVis = useSteppedVisualization({
  totalSteps: shutdownSteps.length,
  autoPlayInterval: 2500,
});
const planVis = useSteppedVisualization({
  totalSteps: planSteps.length,
  autoPlayInterval: 2500,
});

const activeVis = computed(() => (protocol.value === "shutdown" ? shutdownVis : planVis));
const currentStep = computed(() => activeVis.value.currentStep.value);
const totalSteps = computed(() => activeVis.value.totalSteps);
const isPlaying = computed(() => activeVis.value.isPlaying.value);
const current = computed(() => steps.value[currentStep.value]);
const isPlan = computed(() => protocol.value === "plan");
const leaderActive = computed(
  () => (!isPlan.value && (currentStep.value === 1 || currentStep.value === 3)) || (isPlan.value && currentStep.value === 2),
);
const sharedActive = computed(() => currentStep.value === 0);
const teammateActive = computed(() => (!isPlan.value && currentStep.value === 2) || (isPlan.value && currentStep.value === 1));

function next() {
  activeVis.value.next();
}

function prev() {
  activeVis.value.prev();
}

function reset() {
  activeVis.value.reset();
}

function toggleAutoPlay() {
  activeVis.value.toggleAutoPlay();
}

function switchProtocol(value: Protocol) {
  protocol.value = value;
  shutdownVis.reset();
  planVis.reset();
}
</script>

<style scoped>
.team-protocols-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.team-protocols-vis h2 {
  margin: 0;
}

.protocol-panel {
  display: grid;
  gap: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.protocol-toggle {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.protocol-toggle button {
  border: 0;
  border-radius: 6px;
  background: var(--surface-soft);
  color: var(--text-muted);
  padding: 7px 12px;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition:
    background 160ms ease,
    color 160ms ease,
    transform 160ms ease;
}

.protocol-toggle button:hover {
  transform: translateY(-1px);
}

.protocol-toggle button.active {
  background: #2563eb;
  color: #ffffff;
}

.state-rail {
  display: grid;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 12px;
}

.state-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.state-head code {
  overflow-wrap: anywhere;
  color: var(--text-muted);
  font-size: 11px;
}

.state-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  align-items: stretch;
  gap: 8px;
}

.state-card {
  display: grid;
  gap: 5px;
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  color: var(--text-muted);
  padding: 10px;
  transition:
    background 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    transform 180ms ease;
}

.state-card strong,
.state-card span {
  overflow-wrap: anywhere;
}

.state-card strong {
  font-size: 14px;
}

.state-card span {
  font-size: 11px;
  line-height: 1.35;
}

.state-card.active {
  border-color: #60a5fa;
  background: #eff6ff;
  color: #1e40af;
  transform: translateY(-2px);
}

.state-card.done {
  border-color: #34d399;
  background: #ecfdf5;
  color: #047857;
}

.state-arrow {
  display: none;
}

.desk-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.desk {
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 260px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
  transition:
    background 180ms ease,
    border-color 180ms ease;
}

.desk.active {
  border-color: #60a5fa;
  background: #eff6ff;
}

.desk-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.desk-head strong {
  min-width: 0;
  overflow-wrap: anywhere;
}

.desk-icon {
  display: inline-grid;
  flex: 0 0 auto;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 7px;
  background: var(--surface-soft);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 800;
}

.desk.active .desk-icon {
  background: #2563eb;
  color: #ffffff;
}

.tray {
  display: grid;
  gap: 12px;
}

.protocol-card {
  display: grid;
  gap: 5px;
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 12px;
  box-shadow: 0 1px 8px rgba(15, 23, 42, 0.06);
}

.protocol-card strong,
.protocol-card code {
  overflow-wrap: anywhere;
}

.protocol-card strong {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.protocol-card code {
  color: inherit;
  font-size: 11px;
  opacity: 0.88;
}

.tone-blue {
  border-color: #93c5fd;
  background: #eff6ff;
  color: #1e40af;
}

.tone-amber {
  border-color: #fbbf24;
  background: #fffbeb;
  color: #92400e;
}

.tone-emerald {
  border-color: #34d399;
  background: #ecfdf5;
  color: #047857;
}

.tone-zinc {
  border-color: var(--border);
  background: var(--surface-soft);
  color: var(--text);
}

.empty-tray {
  border: 1px dashed var(--border);
  border-radius: 7px;
  color: var(--text-muted);
  padding: 20px 12px;
  text-align: center;
  font-size: 12px;
}

.protocol-note,
.lock-note {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface-soft);
  color: var(--text-muted);
  padding: 10px 12px;
  font-size: 12px;
  line-height: 1.45;
}

.lock-note {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
}

.lock-note span {
  border-radius: 5px;
  background: var(--surface-soft);
  padding: 3px 5px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0;
}

.card-list-enter-active,
.card-list-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.card-list-enter-from,
.card-list-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}

@media (max-width: 920px) {
  .desk-grid {
    grid-template-columns: 1fr;
  }

  .desk {
    min-height: 0;
  }
}

@media (max-width: 720px) {
  .state-head {
    align-items: start;
    flex-direction: column;
  }

  .state-list {
    grid-template-columns: 1fr;
  }
}

@media (prefers-color-scheme: dark) {
  .state-card.active,
  .desk.active,
  .tone-blue {
    border-color: #1d4ed8;
    background: rgba(30, 64, 175, 0.24);
    color: #bfdbfe;
  }

  .state-card.done,
  .tone-emerald {
    border-color: #065f46;
    background: rgba(6, 78, 59, 0.28);
    color: #a7f3d0;
  }

  .tone-amber {
    border-color: #92400e;
    background: rgba(120, 53, 15, 0.24);
    color: #fde68a;
  }
}
</style>
