<template>
  <section class="simulator-panel">
    <h2>Simulator</h2>
    <p>{{ scenario.description }}</p>

    <div class="simulator-shell">
      <div class="simulator-controls">
        <div class="simulator-button-row">
          <button
            type="button"
            :disabled="sim.isComplete.value && !sim.isPlaying.value"
            :title="sim.isPlaying.value ? 'Pause' : 'Play'"
            class="sim-primary-button"
            @click="sim.isPlaying.value ? sim.pause() : sim.play()"
          >
            <svg v-if="sim.isPlaying.value" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 5v14M16 5v14" />
            </svg>
            <svg v-else viewBox="0 0 24 24" aria-hidden="true">
              <path d="m8 5 11 7-11 7z" />
            </svg>
          </button>
          <button type="button" :disabled="sim.isComplete.value" title="Step" @click="sim.stepForward">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m5 4 10 8-10 8zM19 5v14" />
            </svg>
          </button>
          <button type="button" title="Reset" @click="sim.reset">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M3 12a9 9 0 1 0 3-6.7M3 3v6h6" />
            </svg>
          </button>
        </div>
        <div class="speed-tabs">
          <span>Speed:</span>
          <button
            v-for="option in speedOptions"
            :key="option.label"
            :class="{ active: sim.speed.value === option.value }"
            type="button"
            @click="sim.setSpeed(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
        <span class="simulator-count">{{ Math.max(0, sim.currentIndex.value) }} / {{ sim.totalSteps }}</span>
      </div>

      <div class="simulator-feed">
        <p v-if="sim.visibleSteps.value.length === 0" class="empty-state">Press Play or Step to begin</p>
        <article
          v-for="(step, index) in sim.visibleSteps.value"
          :key="`${index}-${step.type}`"
          :class="['simulator-message', `message-${step.type}`]"
        >
          <div class="simulator-message-label">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path :d="messageIconPath(step.type)" />
            </svg>
            <span>
              {{ messageLabel(step.type) }}
              <strong v-if="step.toolName">{{ step.toolName }}</strong>
            </span>
          </div>
          <pre v-if="step.type === 'tool_call' || step.type === 'tool_result' || step.type === 'system_event'">{{
            step.content || "(empty)"
          }}</pre>
          <p v-else>{{ step.content }}</p>
          <small v-if="step.annotation">{{ step.annotation }}</small>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { createSimulatorState } from "@/composables/simulator";
import type { Scenario } from "@/types/agent-data";

const props = defineProps<{ scenario: Scenario }>();
const sim = createSimulatorState(props.scenario.steps);
const speedOptions = [
  { label: "0.5x", value: 1200 },
  { label: "1x", value: 800 },
  { label: "2x", value: 500 },
  { label: "4x", value: 350 },
];
const messageIcons: Record<string, string> = {
  user_message: "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8",
  assistant_text: "M12 8V4H8m8 0h-4m0 0v4M5 8h14v9a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3zM9 13h.01M15 13h.01",
  tool_call: "M14.7 6.3l3 3M5 19l6.5-6.5M13 5l6 6-8 8H5v-6z",
  tool_result: "M5 12h14M13 6l6 6-6 6",
  system_event: "M12 9v4m0 4h.01M10.3 3.9 2 18a2 2 0 0 0 1.7 3h16.6A2 2 0 0 0 22 18L13.7 3.9a2 2 0 0 0-3.4 0z",
};
const messageLabels: Record<string, string> = {
  user_message: "User",
  assistant_text: "Assistant",
  tool_call: "Tool Call",
  tool_result: "Tool Result",
  system_event: "System",
};

watch(
  () => props.scenario.version,
  () => sim.reset(),
);

function messageIconPath(type: string) {
  return messageIcons[type] || messageIcons.assistant_text;
}

function messageLabel(type: string) {
  return messageLabels[type] || "Assistant";
}
</script>
