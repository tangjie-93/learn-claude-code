<template>
  <section class="recovery-vis" data-testid="s11-error-recovery">
    <h2>{{ title || "Error Recovery Paths" }}</h2>
    <div class="recovery-panel">
      <div class="case-grid">
        <article
          v-for="item in cases"
          :key="item.id"
          :data-case="item.id"
          :class="['case-card', item.tone, { active: activeCaseId === item.id, muted: activeCaseId && activeCaseId !== item.id }]"
        >
          <div class="case-head">
            <strong>{{ item.label }}</strong>
            <span v-if="activeCaseId === item.id">recovering</span>
          </div>
          <p>{{ item.symptom }}</p>
          <code>{{ item.action }}</code>
        </article>
      </div>

      <div class="recovery-grid">
        <article class="state-panel">
          <h3>RecoveryState</h3>
          <div class="state-list">
            <div v-for="entry in stateEntries" :key="entry.label" class="state-row">
              <span>{{ entry.label }}</span>
              <strong>{{ entry.value }}</strong>
            </div>
          </div>
        </article>

        <article class="action-panel">
          <h3>{{ action.title }}</h3>
          <p>{{ action.description }}</p>
          <code v-for="line in action.lines" :key="line">{{ line }}</code>
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

defineProps<{ title?: string }>();

const steps = [
  {
    title: "Normal Call Still Comes First",
    desc: "The runtime starts with a regular LLM call and only enters recovery when a specific failure appears.",
    mode: "normal",
  },
  {
    title: "max_tokens Means Output Was Cut Off",
    desc: "First recovery is to retry with a larger budget before adding any synthetic continuation message.",
    mode: "max-tokens",
  },
  {
    title: "prompt_too_long Means Context Must Shrink",
    desc: "The runtime performs reactive compact once, then retries the same task with a smaller message list.",
    mode: "prompt-too-long",
  },
  {
    title: "429 Means Wait, Then Retry",
    desc: "Rate limits use exponential backoff with jitter so retries do not overload the provider.",
    mode: "rate-limit",
  },
  {
    title: "Repeated 529 Can Switch Models",
    desc: "Provider overload increments RecoveryState and can move to a fallback model after repeated failures.",
    mode: "overloaded",
  },
  {
    title: "Recovered Calls Return to the Loop",
    desc: "Every recovery path is bounded, inspectable, and returns to the normal loop or exits cleanly.",
    mode: "summary",
  },
] as const;

const cases = [
  {
    id: "max-tokens",
    label: "max_tokens",
    symptom: "model stopped mid-answer",
    action: "8K -> 64K, retry same request",
    tone: "amber",
  },
  {
    id: "prompt-too-long",
    label: "prompt_too_long",
    symptom: "context too large",
    action: "reactive_compact(messages), retry once",
    tone: "orange",
  },
  {
    id: "rate-limit",
    label: "429",
    symptom: "rate limited",
    action: "backoff + jitter, max 10 retries",
    tone: "blue",
  },
  {
    id: "overloaded",
    label: "529",
    symptom: "provider overloaded",
    action: "backoff; 3 consecutive -> fallback model",
    tone: "red",
  },
] as const;

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2600,
});

const current = computed(() => steps[currentStep.value]);
const activeCaseId = computed(() => {
  if (current.value.mode === "max-tokens") return "max-tokens";
  if (current.value.mode === "prompt-too-long") return "prompt-too-long";
  if (current.value.mode === "rate-limit") return "rate-limit";
  if (current.value.mode === "overloaded") return "overloaded";
  return null;
});

const stateEntries = computed(() => [
  { label: "max_tokens", value: current.value.mode === "max-tokens" || current.value.mode === "summary" ? "64K used" : "8K" },
  {
    label: "reactive_compact",
    value: current.value.mode === "prompt-too-long" || current.value.mode === "summary" ? "used once" : "unused",
  },
  {
    label: "retry_attempt",
    value: ["rate-limit", "overloaded", "summary"].includes(current.value.mode) ? "counting" : "0",
  },
  { label: "current_model", value: current.value.mode === "overloaded" ? "fallback model ready" : "primary" },
]);

const action = computed(() => {
  if (current.value.mode === "max-tokens") {
    return {
      title: "Escalate output budget",
      description: "No fake continue message on the first escalation.",
      lines: ["before: max_tokens=8000", "retry: max_tokens=64000"],
    };
  }
  if (current.value.mode === "prompt-too-long") {
    return {
      title: "Shrink context, retry once",
      description: "If it is still too long after compact, exit cleanly.",
      lines: ["messages = reactive_compact(messages)"],
    };
  }
  if (current.value.mode === "rate-limit") {
    return {
      title: "Exponential backoff",
      description: "Wait before retrying so the provider has time to recover.",
      lines: ["0.5s + jitter", "1s + jitter", "2s + jitter"],
    };
  }
  if (current.value.mode === "overloaded") {
    return {
      title: "Fallback model path",
      description: "Repeated provider overload can switch to a fallback model.",
      lines: ["consecutive_529 >= 3", "current_model = FALLBACK_MODEL_ID"],
    };
  }
  if (current.value.mode === "summary") {
    return {
      title: "Continue or exit cleanly",
      description: "Each path has a limit, then returns to the normal loop or stops with an explicit error.",
      lines: cases.map((item) => `${item.label}: bounded`),
    };
  }
  return {
    title: "Normal tool loop",
    description: "LLM succeeds, function_call continues as usual.",
    lines: ["response = client.responses.create(...)", "execute function_call outputs"],
  };
});
</script>

<style scoped>
.recovery-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.recovery-vis h2,
.state-panel h3,
.action-panel h3 {
  margin: 0;
}

.recovery-panel,
.state-panel,
.action-panel {
  display: grid;
  gap: 14px;
}

.recovery-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.case-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.case-card,
.state-panel,
.action-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
}

.case-card {
  display: grid;
  gap: 8px;
  transition: transform 0.2s ease, opacity 0.2s ease, border-color 0.2s ease;
}

.case-card.active {
  transform: translateY(-2px);
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 10%, var(--surface));
}

.case-card.muted {
  opacity: 0.5;
}

.case-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.case-head strong,
.case-card code,
.state-row span,
.action-panel code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.case-head strong {
  font-size: 13px;
}

.case-head span {
  border-radius: 999px;
  background: var(--accent);
  color: white;
  padding: 2px 7px;
  font-size: 11px;
}

.case-card p,
.action-panel p {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.case-card code,
.action-panel code {
  display: block;
  border-radius: 6px;
  background: var(--surface-soft);
  padding: 7px;
  color: var(--text);
  font-size: 11px;
  white-space: normal;
}

.recovery-grid {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 12px;
}

.state-list {
  display: grid;
  gap: 8px;
}

.state-row {
  display: grid;
  gap: 4px;
  border-radius: 7px;
  background: var(--surface-soft);
  padding: 10px;
}

.state-row span {
  color: var(--text-muted);
  font-size: 11px;
}

.state-row strong {
  font-size: 14px;
}

@media (max-width: 900px) {
  .case-grid,
  .recovery-grid {
    grid-template-columns: 1fr;
  }
}
</style>
