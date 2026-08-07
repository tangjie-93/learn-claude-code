<template>
  <div class="step-controls">
    <div class="step-copy">
      <strong>{{ stepTitle }}</strong>
      <p>{{ stepDescription }}</p>
    </div>
    <div class="step-actions">
      <div class="step-buttons">
        <button type="button" title="Reset" @click="$emit('reset')">Reset</button>
        <button type="button" title="Previous step" :disabled="currentStep === 0" @click="$emit('prev')">
          Prev
        </button>
        <button type="button" :title="isPlaying ? 'Pause' : 'Auto-play'" @click="$emit('toggle')">
          {{ isPlaying ? "Pause" : "Play" }}
        </button>
        <button
          type="button"
          title="Next step"
          :disabled="currentStep === totalSteps - 1"
          @click="$emit('next')"
        >
          Next
        </button>
      </div>
      <div class="step-progress" aria-label="Visualization progress">
        <span
          v-for="index in totalSteps"
          :key="index"
          :class="{ active: index - 1 === currentStep, done: index - 1 < currentStep }"
        />
        <em>{{ currentStep + 1 }}/{{ totalSteps }}</em>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  reset: [];
  prev: [];
  toggle: [];
  next: [];
}>();

defineProps<{
  currentStep: number;
  totalSteps: number;
  isPlaying: boolean;
  stepTitle: string;
  stepDescription: string;
}>();
</script>
