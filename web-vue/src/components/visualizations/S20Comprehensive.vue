<template>
  <section class="comprehensive-vis" data-testid="s20-comprehensive">
    <h2>{{ title || "Comprehensive Agent Turn" }}</h2>
    <div class="comp-panel">
      <div class="comp-grid">
        <article class="journey-column">
          <div class="section-head">
            <span>BOT</span>
            <h3>One-turn journey</h3>
          </div>
          <div class="stage-list">
            <div
              v-for="(stage, index) in stages"
              :key="stage.id"
              :data-stage="stage.id"
              :class="['stage-node', { active: index === currentStageIndex, done: index < currentStageIndex }]"
            >
              <span class="stage-icon">{{ index < currentStageIndex ? "OK" : stage.icon }}</span>
              <div>
                <strong>{{ index + 1 }}. {{ stage.label }}</strong>
                <small>{{ stage.detail }}</small>
              </div>
            </div>
          </div>
        </article>

        <div class="packet-column">
          <article class="packet-card">
            <div class="packet-head">
              <div class="section-head">
                <span>PKT</span>
                <h3>Turn packet</h3>
              </div>
              <code>step {{ currentStep + 1 }}/{{ totalSteps }}</code>
            </div>

            <div class="packet-lines">
              <div class="packet-line blue">
                <small>request</small>
                <strong>{{ current.packet.request }}</strong>
              </div>
              <div class="packet-split">
                <div class="context-card">
                  <small>carried context</small>
                  <div class="context-tags">
                    <span v-for="item in current.packet.carried" :key="item">{{ item }}</span>
                  </div>
                </div>
                <div class="packet-line">
                  <small>decision</small>
                  <strong>{{ current.packet.decision }}</strong>
                </div>
              </div>
              <div class="packet-line emerald">
                <small>result</small>
                <strong>{{ current.packet.result }}</strong>
              </div>
            </div>
          </article>

          <article class="transcript-card">
            <div class="section-head">
              <span>TXT</span>
              <h3>Source-of-truth transcript</h3>
            </div>
            <div class="transcript-list">
              <div v-for="item in current.transcript" :key="item" class="transcript-row">{{ item }}</div>
            </div>
          </article>
        </div>
      </div>

      <div class="surface-grid">
        <div v-for="surface in surfaces" :key="surface.label" class="surface-card">
          <div class="surface-head">
            <span>{{ surface.icon }}</span>
            <strong>{{ surface.label }}</strong>
          </div>
          <p>{{ surface.text }}</p>
        </div>
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

type StageId = "intake" | "guardrails" | "route" | "execute" | "external" | "recover" | "append";

interface Stage {
  id: StageId;
  label: string;
  detail: string;
  icon: string;
}

interface StepState {
  title: string;
  desc: string;
  stage: StageId;
  packet: {
    request: string;
    carried: string[];
    decision: string;
    result: string;
  };
  transcript: string[];
}

defineProps<{ title?: string }>();

const stages: Stage[] = [
  { id: "intake", label: "Intake", detail: "request, memory, background notes", icon: "IN" },
  { id: "guardrails", label: "Guardrails", detail: "permissions, hooks, policy", icon: "GD" },
  { id: "route", label: "Route", detail: "choose the right work surface", icon: "RT" },
  { id: "execute", label: "Execute", detail: "local tools, teams, worktrees", icon: "EX" },
  { id: "external", label: "External", detail: "MCP toolboxes return results", icon: "MC" },
  { id: "recover", label: "Recover", detail: "retry, compact, repair state", icon: "RC" },
  { id: "append", label: "Append", detail: "one transcript stays authoritative", icon: "AP" },
];

const surfaces = [
  { label: "background", icon: "BG", text: "slow commands can finish later" },
  { label: "team", icon: "TM", text: "teammates work through mailboxes" },
  { label: "worktree", icon: "WT", text: "risky edits stay isolated" },
  { label: "MCP", icon: "MP", text: "external tools are normalized" },
];

const steps: StepState[] = [
  {
    title: "A Turn Starts as a Packet",
    desc: "The comprehensive agent first gathers everything the model should see, instead of scattering context across hidden places.",
    stage: "intake",
    packet: {
      request: "Fix the web lesson visuals and verify the pages.",
      carried: ["recent messages", "relevant memory", "background notes"],
      decision: "build one model-visible input packet",
      result: "ready for a model call",
    },
    transcript: ["user request enters", "memory and notes are attached"],
  },
  {
    title: "Guardrails Check the Packet",
    desc: "Permissions and hooks are the inspection gate before work happens.",
    stage: "guardrails",
    packet: {
      request: "Edit files, run build, open browser.",
      carried: ["permission mode", "hook output", "workspace rules"],
      decision: "allowed work continues; risky work asks first",
      result: "safe action envelope",
    },
    transcript: ["policy checked", "allowed actions are visible"],
  },
  {
    title: "The Agent Picks Work Surfaces",
    desc: "The model chooses the smallest surface that matches the job.",
    stage: "route",
    packet: {
      request: "Search code, patch UI, verify rendered pages.",
      carried: ["available tools", "team status", "MCP registry"],
      decision: "local edit first, external tools only when needed",
      result: "work split into clear lanes",
    },
    transcript: ["route: code search", "route: browser check", "route: no teammate needed"],
  },
  {
    title: "Work Runs in Bounded Places",
    desc: "Tools, teammates, and worktrees all produce small result cards.",
    stage: "execute",
    packet: {
      request: "Apply the patch and run the build.",
      carried: ["tool call", "worktree lane", "expected output"],
      decision: "execute, then return summarized results",
      result: "local evidence collected",
    },
    transcript: ["patch applied", "build output summarized"],
  },
  {
    title: "External Results Re-enter the Same Lane",
    desc: "MCP tools expand capability, but return as ordinary tool results.",
    stage: "external",
    packet: {
      request: "Use an external source or tool if local context is missing.",
      carried: ["MCP tool name", "structured arguments", "returned artifact"],
      decision: "normalize external output before the next model step",
      result: "outside work is no longer special",
    },
    transcript: ["MCP result received", "result card appended"],
  },
  {
    title: "Recovery Keeps the Turn Understandable",
    desc: "Long context, command errors, and retries are handled as named recovery moves.",
    stage: "recover",
    packet: {
      request: "If context or execution gets messy, repair before continuing.",
      carried: ["error text", "retry count", "compact summary"],
      decision: "retry once, compact old detail, keep the reason visible",
      result: "the turn remains legible",
    },
    transcript: ["error classified", "recovery note added", "work resumes"],
  },
  {
    title: "Everything Writes Back to One Transcript",
    desc: "All mechanisms eventually append evidence to the same source of truth.",
    stage: "append",
    packet: {
      request: "Report what changed and what was verified.",
      carried: ["tool evidence", "browser checks", "remaining risks"],
      decision: "answer from the transcript, not from memory alone",
      result: "next turn has a clean starting point",
    },
    transcript: ["tests pass", "visual checks recorded", "final answer drafted"],
  },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2800,
});

const current = computed(() => steps[currentStep.value]);
const currentStageIndex = computed(() => stages.findIndex((stage) => stage.id === current.value.stage));
</script>

<style scoped>
.comprehensive-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.comprehensive-vis h2,
.journey-column h3,
.section-head h3 {
  margin: 0;
}

.comp-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.comp-grid {
  display: grid;
  grid-template-columns: 0.9fr 1.2fr;
  gap: 14px;
}

.journey-column,
.packet-card,
.transcript-card,
.surface-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
  padding: 12px;
}

.section-head,
.surface-head {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.section-head span,
.surface-head span,
.stage-icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex: none;
  border-radius: 7px;
  background: var(--surface);
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 800;
}

.stage-list,
.packet-column,
.packet-lines,
.transcript-list {
  display: grid;
  gap: 10px;
}

.stage-list {
  margin-top: 12px;
}

.stage-node {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: center;
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 10px;
}

.stage-node strong,
.stage-node small {
  display: block;
  overflow-wrap: anywhere;
}

.stage-node small {
  margin-top: 2px;
  color: var(--text-muted);
  line-height: 1.35;
}

.stage-node.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.stage-node.done {
  border-color: #10b981;
  background: #ecfdf5;
  color: #047857;
}

.stage-node.active .stage-icon {
  background: #3b82f6;
  color: white;
}

.stage-node.done .stage-icon {
  background: #10b981;
  color: white;
}

.packet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.packet-head code {
  flex: none;
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-muted);
  padding: 5px 8px;
  font-size: 11px;
}

.packet-lines {
  margin-top: 12px;
}

.packet-split,
.surface-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.packet-line,
.context-card,
.transcript-row {
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--surface);
  padding: 10px;
  overflow-wrap: anywhere;
}

.packet-line small,
.context-card small {
  display: block;
  margin-bottom: 7px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
  text-transform: uppercase;
}

.packet-line strong {
  line-height: 1.35;
}

.packet-line.blue {
  border-color: #93c5fd;
  background: #eff6ff;
  color: #1d4ed8;
}

.packet-line.emerald {
  border-color: #86efac;
  background: #ecfdf5;
  color: #047857;
}

.context-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.context-tags span {
  border-radius: 6px;
  background: var(--surface-soft);
  padding: 4px 7px;
  font-size: 11px;
  overflow-wrap: anywhere;
}

.transcript-card {
  background: var(--surface);
}

.transcript-list {
  margin-top: 10px;
}

.transcript-row {
  background: var(--surface-soft);
  font-size: 12px;
  color: var(--text);
}

.surface-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.surface-card p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.4;
}

@media (max-width: 900px) {
  .comp-grid,
  .surface-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .comp-panel {
    padding: 12px;
  }

  .packet-head,
  .packet-split {
    grid-template-columns: 1fr;
  }

  .packet-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
