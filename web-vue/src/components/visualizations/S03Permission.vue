<template>
  <section class="permission-vis" data-testid="s03-permission">
    <h2>{{ title || "Permission Desk" }}</h2>

    <div class="stage">
      <div class="surfaces">
        <article :class="surfaceClass(currentMode === 'overview' || activeId !== null)">
          <div class="surface-title">
            <span class="surface-icon">!</span>
            <span>Tool requests</span>
          </div>

          <div class="request-list">
            <div
              v-for="request in REQUESTS"
              :key="request.id"
              :class="requestClass(request, activeId === request.id || (currentMode === 'overview' && currentStep === 0), activeId !== null && activeId !== request.id)"
            >
              <div class="request-head">
                <span>tool request</span>
                <span class="pill mono">{{ request.tool }}</span>
              </div>
              <code>{{ request.command }}</code>
              <div class="request-foot">
                <span>{{ request.detail }}</span>
                <span class="result">{{ request.result }}</span>
              </div>
            </div>
          </div>
        </article>

        <article :class="surfaceClass(currentMode !== 'overview')">
          <div class="surface-title">
            <span class="surface-icon">OK</span>
            <span>Permission desk</span>
          </div>

          <div class="check-list">
            <template v-if="currentMode === 'overview' || currentMode === 'summary'">
              <CheckRow label="Safe read" detail="No write, no shell, no approval needed." status="allow" :active="currentMode === 'overview'" />
              <CheckRow label="Risky local change" detail="May be useful, but requires a human yes." status="ask" :active="currentMode === 'overview'" />
              <CheckRow label="Forbidden pattern" detail="Root delete and sudo never reach handlers." status="deny" :active="currentMode === 'overview'" />
            </template>

            <template v-else-if="currentMode === 'allow'">
              <CheckRow label="Gate 1: hard deny" detail="No sudo, no root path, no forbidden pattern." status="pass" :active="false" />
              <CheckRow label="Gate 2: allow rule" detail="Read-only workspace file can run immediately." status="allow" active />
              <CheckRow label="Gate 3: user approval" detail="Skipped because this call is already safe." status="skip" :active="false" />
            </template>

            <template v-else-if="currentMode === 'deny'">
              <CheckRow label="Gate 1: hard deny" detail="sudo + root delete is blocked immediately." status="deny" active />
              <CheckRow label="Gate 2: risk rule" detail="Skipped because hard deny already decided." status="skip" :active="false" />
              <CheckRow label="Gate 3: user approval" detail="Skipped because the user cannot approve forbidden actions." status="skip" :active="false" />
            </template>

            <template v-else>
              <CheckRow label="Gate 1: hard deny" detail="Local project path is not globally forbidden." status="pass" :active="false" />
              <CheckRow label="Gate 2: risk rule" detail="Deleting files needs an explicit approval ticket." status="ask" :active="currentMode === 'ask'" />
              <CheckRow
                label="Gate 3: user approval"
                detail="The tool waits until this request is approved."
                :status="currentMode === 'ask-approved' ? 'approved' : 'waiting'"
                :active="currentMode === 'ask-approved'"
              />
            </template>
          </div>
        </article>

        <article :class="surfaceClass(currentMode !== 'overview')">
          <div class="surface-title">
            <span class="surface-icon">RUN</span>
            <span>Outcome</span>
          </div>

          <Transition name="fade-slide" mode="out-in">
            <div :key="currentMode" class="outcome">
              <div v-if="currentMode === 'overview'" class="empty-outcome">select a request route</div>

              <div v-else-if="currentMode === 'allow'" class="outcome-card tone-emerald">
                <div class="outcome-title">Handler runs now</div>
                <CodeLine label="handler" value="read_file" />
                <CodeLine label="args" value='path: "README.md"' />
              </div>

              <div v-else-if="currentMode === 'ask'" class="outcome-card tone-amber">
                <div class="outcome-title">Approval ticket</div>
                <p>"Allow deleting local build cache?"</p>
              </div>

              <div v-else-if="currentMode === 'ask-approved'" class="outcome-card tone-blue">
                <div class="outcome-title">Handler runs after approval</div>
                <CodeLine label="handler" value="bash" />
                <CodeLine label="args" value="rm -rf ./tmp/build-cache" />
              </div>

              <div v-else-if="currentMode === 'deny'" class="outcome-card tone-red">
                <div class="outcome-title">Blocked before handler</div>
                <p>No tool execution, no user prompt, no filesystem touch.</p>
              </div>

              <div v-else class="summary-list">
                <div v-for="request in REQUESTS" :key="request.id" :class="['summary-card', `tone-${request.tone}`]">
                  <div class="summary-result">{{ request.result }}</div>
                  <p>{{ request.detail }}</p>
                </div>
                <div class="outcome-card tone-emerald">
                  <div class="outcome-title">decision returned to loop</div>
                  <p>
                    Permission stays outside the model, but the loop still receives a normal tool_result or
                    blocked result.
                  </p>
                </div>
              </div>
            </div>
          </Transition>
        </article>
      </div>

      <div class="rule-note">
        Beginner rule: the model proposes tools; the runtime routes each request to allow, ask, or deny before
        execution.
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
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

const STEPS = [
  {
    title: "Three Requests, Three Routes",
    desc: "Permission is a router: safe calls run, risky calls ask, forbidden calls stop.",
    mode: "overview",
  },
  {
    title: "Allow: Safe Read Runs Immediately",
    desc: "A read-only file request passes policy and reaches the handler without a user ticket.",
    mode: "allow",
  },
  {
    title: "Ask: Risky Local Delete Becomes a Ticket",
    desc: "A local delete command is not forbidden, but it must pause for explicit confirmation.",
    mode: "ask",
  },
  {
    title: "Approved Ask: Handler Runs After Yes",
    desc: "The same risky request executes only after the user approves this exact action.",
    mode: "ask-approved",
  },
  {
    title: "Deny: Forbidden Pattern Stops Early",
    desc: "A root-level sudo delete is blocked before any handler can touch the machine.",
    mode: "deny",
  },
  {
    title: "One Permission Desk, Three Outcomes",
    desc: "The harness keeps allow, ask, and deny decisions outside the model, then returns the decision to the loop.",
    mode: "summary",
  },
] as const;

const REQUESTS = [
  {
    id: "allow",
    tool: "read_file",
    command: "README.md",
    result: "allow",
    detail: "read-only workspace file",
    tone: "emerald",
  },
  {
    id: "ask",
    tool: "bash",
    command: "rm -rf ./tmp/build-cache",
    result: "ask",
    detail: "local destructive command",
    tone: "amber",
  },
  {
    id: "deny",
    tool: "bash",
    command: "sudo rm -rf /",
    result: "deny",
    detail: "forbidden root delete",
    tone: "red",
  },
] as const;

type StepMode = (typeof STEPS)[number]["mode"];
type Request = (typeof REQUESTS)[number];
type RequestId = Request["id"];
type CheckStatus = "waiting" | "pass" | "allow" | "ask" | "approved" | "deny" | "skip";
type Tone = Request["tone"] | "blue" | "zinc";

defineProps<{
  title?: string;
}>();

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEPS.length,
  autoPlayInterval: 2500,
});

const current = computed(() => STEPS[currentStep.value]);
const currentMode = computed(() => current.value.mode);
const activeId = computed(() => activeRequestId(currentMode.value));

function activeRequestId(stepMode: StepMode): RequestId | null {
  if (stepMode === "allow") return "allow";
  if (stepMode === "ask" || stepMode === "ask-approved") return "ask";
  if (stepMode === "deny") return "deny";
  return null;
}

function statusTone(status: CheckStatus): Tone {
  if (status === "deny") return "red";
  if (status === "pass" || status === "allow" || status === "approved") return "emerald";
  if (status === "ask") return "amber";
  return "zinc";
}

function surfaceClass(active: boolean) {
  return ["surface", { active }];
}

function requestClass(request: Request, active: boolean, muted: boolean) {
  return ["request-card", `tone-${active ? request.tone : "zinc"}`, { active, muted }];
}

function checkClass(status: CheckStatus, active: boolean) {
  return ["check-row", `tone-${active ? statusTone(status) : "zinc"}`, { active }];
}

function statusIcon(status: CheckStatus) {
  if (status === "deny") return "!";
  if (status === "pass" || status === "allow") return "OK";
  if (status === "ask") return "?";
  if (status === "approved") return "YES";
  return "...";
}

const CheckRow = defineComponent({
  props: {
    label: { type: String, required: true },
    detail: { type: String, required: true },
    status: { type: String as () => CheckStatus, required: true },
    active: { type: Boolean, default: false },
  },
  setup(props) {
    return () =>
      h("div", { class: checkClass(props.status, props.active) }, [
        h("div", { class: "check-head" }, [
          h("div", { class: "check-label" }, [
            h("span", { class: "status-icon" }, statusIcon(props.status)),
            h("span", props.label),
          ]),
          h("span", { class: "status-pill" }, props.status),
        ]),
        h("div", { class: "check-detail" }, props.detail),
      ]);
  },
});

const CodeLine = defineComponent({
  props: {
    label: { type: String, required: true },
    value: { type: String, required: true },
  },
  setup(props) {
    return () =>
      h("div", { class: "code-line" }, [
        h("div", { class: "code-label" }, props.label),
        h("code", props.value),
      ]);
  },
});
</script>

<style scoped>
.permission-vis {
  min-height: 500px;
}

.permission-vis h2 {
  margin: 0 0 16px;
  color: #18181b;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.stage {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.surfaces {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
}

.surface {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.surface.active {
  border-color: #fca5a5;
  background: #fef2f2;
}

.surface-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  color: #18181b;
  font-size: 18px;
  font-weight: 650;
}

.surface-icon {
  display: inline-flex;
  width: 40px;
  height: 40px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f4f4f5;
  color: #71717a;
  font-size: 11px;
  font-weight: 750;
}

.surface.active .surface-icon {
  background: #ef4444;
  color: #ffffff;
}

.request-list,
.check-list,
.summary-list {
  display: grid;
  gap: 8px;
}

.request-card {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 12px;
  background: #ffffff;
  padding: 16px;
  color: #3f3f46;
  box-shadow: 0 1px 2px rgba(24, 24, 27, 0.08);
  transition:
    opacity 180ms ease,
    transform 180ms ease,
    background-color 180ms ease,
    border-color 180ms ease;
}

.request-card.active {
  transform: translateY(-1px);
}

.request-card.muted {
  opacity: 0.45;
}

.request-head,
.request-foot,
.check-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.request-head {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 650;
}

.request-card code {
  display: block;
  min-width: 0;
  border-radius: 8px;
  background: #09090b;
  padding: 12px;
  color: #f4f4f5;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.55;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.request-foot {
  margin-top: 12px;
  font-size: 14px;
}

.pill,
.result,
.status-pill {
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 700;
}

.result,
.status-pill {
  border-radius: 4px;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.check-row,
.summary-card,
.outcome-card {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
  color: #3f3f46;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.outcome-card {
  border-radius: 12px;
  padding: 16px;
}

.check-label,
.outcome-title,
.summary-result {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
}

.outcome-title {
  margin-bottom: 12px;
  font-size: 16px;
}

.status-icon {
  display: inline-flex;
  min-width: 18px;
  justify-content: center;
  font-size: 11px;
  font-weight: 750;
}

.check-detail,
.summary-card p,
.outcome-card p {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.55;
  opacity: 0.82;
}

.outcome-card p {
  font-size: 14px;
}

.empty-outcome {
  border: 1px dashed #d4d4d8;
  border-radius: 8px;
  padding: 32px 16px;
  color: #71717a;
  font-size: 14px;
  text-align: center;
}

.code-line {
  min-width: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  padding: 8px;
}

.code-line + .code-line {
  margin-top: 12px;
}

.code-label {
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  opacity: 0.7;
  text-transform: uppercase;
}

.code-line code {
  display: block;
  min-width: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.55;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.tone-emerald {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #065f46;
}

.tone-amber {
  border-color: #fde68a;
  background: #fffbeb;
  color: #92400e;
}

.tone-red {
  border-color: #fecaca;
  background: #fef2f2;
  color: #991b1b;
}

.tone-blue {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.tone-zinc {
  border-color: #e4e4e7;
  background: #ffffff;
  color: #3f3f46;
}

.rule-note {
  margin-top: 12px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #fafafa;
  padding: 12px 16px;
  color: #52525b;
  font-size: 14px;
  line-height: 1.55;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition:
    opacity 160ms ease,
    transform 160ms ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
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
  padding: 6px 10px;
  color: #27272a;
  font: inherit;
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

:deep(.step-progress span.done),
:deep(.step-progress span.active) {
  background: #ef4444;
}

:deep(.step-progress em) {
  margin-left: 6px;
  color: #52525b;
  font-size: 12px;
  font-style: normal;
  font-weight: 700;
}

@media (min-width: 1024px) {
  .surfaces {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr) minmax(0, 0.95fr);
  }

  :deep(.step-controls) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  :deep(.step-actions) {
    align-items: flex-end;
  }
}

@media (prefers-color-scheme: dark) {
  .permission-vis h2,
  .surface-title,
  :deep(.step-copy strong) {
    color: #f4f4f5;
  }

  .stage,
  .surface,
  .tone-zinc,
  :deep(.step-controls),
  :deep(.step-buttons button) {
    border-color: #3f3f46;
    background: #18181b;
    color: #e4e4e7;
  }

  .surface.active {
    border-color: #7f1d1d;
    background: rgba(127, 29, 29, 0.3);
  }

  .surface-icon {
    background: #27272a;
    color: #d4d4d8;
  }

  .rule-note {
    border-color: #3f3f46;
    background: rgba(39, 39, 42, 0.7);
    color: #d4d4d8;
  }

  .empty-outcome {
    border-color: #3f3f46;
    color: #a1a1aa;
  }

  .tone-emerald {
    border-color: #064e3b;
    background: rgba(6, 78, 59, 0.4);
    color: #a7f3d0;
  }

  .tone-amber {
    border-color: #78350f;
    background: rgba(120, 53, 15, 0.4);
    color: #fde68a;
  }

  .tone-red {
    border-color: #7f1d1d;
    background: rgba(127, 29, 29, 0.4);
    color: #fecaca;
  }

  .tone-blue {
    border-color: #1e3a8a;
    background: rgba(30, 58, 138, 0.4);
    color: #bfdbfe;
  }

  :deep(.step-copy p),
  :deep(.step-progress em) {
    color: #d4d4d8;
  }

  :deep(.step-progress span) {
    background: #3f3f46;
  }
}
</style>
