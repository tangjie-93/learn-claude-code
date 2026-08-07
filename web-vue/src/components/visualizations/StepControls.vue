<template>
  <div class="step-controls">
    <div class="step-copy">
      <strong>{{ stepTitle }}</strong>
      <p>{{ stepDescription }}</p>
    </div>
    <div class="step-actions">
      <div class="step-buttons">
        <button type="button" title="Reset" @click="$emit('reset')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M3 12a9 9 0 1 0 3-6.7" />
            <path d="M3 4v6h6" />
          </svg>
        </button>
        <button type="button" title="Previous step" :disabled="currentStep === 0" @click="$emit('prev')">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M19 20 9 12l10-8v16Z" />
            <path d="M5 19V5" />
          </svg>
        </button>
        <button type="button" :title="isPlaying ? 'Pause' : 'Auto-play'" @click="$emit('toggle')">
          <svg v-if="isPlaying" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M8 5v14" />
            <path d="M16 5v14" />
          </svg>
          <svg v-else viewBox="0 0 24 24" aria-hidden="true">
            <path d="m8 5 11 7-11 7V5Z" />
          </svg>
        </button>
        <button
          type="button"
          title="Next step"
          :disabled="currentStep === totalSteps - 1"
          @click="$emit('next')"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="m5 4 10 8-10 8V4Z" />
            <path d="M19 5v14" />
          </svg>
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
