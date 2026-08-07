import { computed, onBeforeUnmount, ref } from "vue";

interface SteppedVisualizationOptions {
  totalSteps: number;
  autoPlayInterval?: number;
  initialStep?: number;
}

export function useSteppedVisualization({
  totalSteps,
  autoPlayInterval = 2000,
  initialStep = 0,
}: SteppedVisualizationOptions) {
  function clamp(step: number) {
    return Math.max(0, Math.min(step, totalSteps - 1));
  }

  const currentStep = ref(clamp(initialStep));
  const isPlaying = ref(false);
  let timer: ReturnType<typeof setInterval> | undefined;

  function clearTimer() {
    if (timer) {
      clearInterval(timer);
      timer = undefined;
    }
  }

  function next() {
    currentStep.value = clamp(currentStep.value + 1);
    if (currentStep.value >= totalSteps - 1) {
      isPlaying.value = false;
      clearTimer();
    }
  }

  function prev() {
    currentStep.value = clamp(currentStep.value - 1);
  }

  function reset() {
    currentStep.value = 0;
    isPlaying.value = false;
    clearTimer();
  }

  function goToStep(step: number) {
    currentStep.value = clamp(step);
  }

  function toggleAutoPlay() {
    isPlaying.value = !isPlaying.value;
    clearTimer();
    if (isPlaying.value) {
      timer = setInterval(next, autoPlayInterval);
    }
  }

  onBeforeUnmount(clearTimer);

  return {
    currentStep,
    totalSteps,
    next,
    prev,
    reset,
    goToStep,
    isPlaying,
    toggleAutoPlay,
    isFirstStep: computed(() => currentStep.value === 0),
    isLastStep: computed(() => currentStep.value === totalSteps - 1),
  };
}
