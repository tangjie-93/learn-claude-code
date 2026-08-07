<template>
  <section class="simple-panel simulator-panel">
    <div class="simulator-heading">
      <div>
        <h2>Simulator</h2>
        <p>{{ scenario.description }}</p>
      </div>
      <span>{{ sim.currentIndex.value }} / {{ sim.totalSteps }}</span>
    </div>

    <div class="simulator-controls">
      <button type="button" :disabled="sim.isComplete.value" @click="sim.isPlaying.value ? sim.pause() : sim.play()">
        {{ sim.isPlaying.value ? "Pause" : "Play" }}
      </button>
      <button type="button" :disabled="sim.isComplete.value" @click="sim.stepForward">Step</button>
      <button type="button" @click="sim.reset">Reset</button>
      <label>
        Speed
        <select :value="sim.speed.value" @change="onSpeedChange">
          <option :value="1200">Slow</option>
          <option :value="800">Normal</option>
          <option :value="350">Fast</option>
        </select>
      </label>
    </div>

    <div class="simulator-feed">
      <p v-if="sim.visibleSteps.value.length === 0" class="empty-state">Press Play or Step to begin</p>
      <article
        v-for="(step, index) in sim.visibleSteps.value"
        :key="`${index}-${step.type}`"
        :class="['simulator-message', `message-${step.type}`]"
      >
        <span>{{ step.type }}</span>
        <p>{{ step.content }}</p>
        <small v-if="step.annotation">{{ step.annotation }}</small>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { watch } from "vue";
import { createSimulatorState } from "@/composables/simulator";
import type { Scenario } from "@/types/agent-data";

const props = defineProps<{ scenario: Scenario }>();
const sim = createSimulatorState(props.scenario.steps);

watch(
  () => props.scenario.version,
  () => sim.reset(),
);

function onSpeedChange(event: Event) {
  sim.setSpeed(Number((event.target as HTMLSelectElement).value));
}
</script>
