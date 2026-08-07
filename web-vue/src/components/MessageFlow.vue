<template>
  <div class="message-flow">
    <div class="message-flow-header">
      <span>messages[]</span>
      <strong>len={{ count }}</strong>
    </div>
    <div class="message-flow-track">
      <TransitionGroup name="message-flow-item">
        <span
          v-for="(step, index) in visibleSteps"
          :key="`${step.label}-${index}`"
          :class="['message-token', `message-token-${step.role}`]"
        >
          {{ step.label }}
        </span>
      </TransitionGroup>
      <span v-if="count === 0" class="message-empty">[]</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const steps = [
  { role: "user", label: "user" },
  { role: "assistant", label: "assistant" },
  { role: "tool-call", label: "tool_call" },
  { role: "tool-result", label: "tool_result" },
  { role: "assistant", label: "assistant" },
  { role: "tool-call", label: "tool_call" },
  { role: "tool-result", label: "tool_result" },
  { role: "assistant", label: "assistant (final)" },
];

const count = ref(0);
let timer: number | undefined;

const visibleSteps = computed(() => steps.slice(0, count.value));

onMounted(() => {
  timer = window.setInterval(() => {
    if (count.value >= steps.length) {
      window.setTimeout(() => {
        count.value = 0;
      }, 1500);
      return;
    }
    count.value += 1;
  }, 800);
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});
</script>
