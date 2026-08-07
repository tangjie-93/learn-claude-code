import { computed, ref, type Ref } from "vue";
import type { ScenarioStep } from "@/types/agent-data";

export interface SimulatorState {
  currentIndex: Ref<number>;
  isPlaying: Ref<boolean>;
  speed: Ref<number>;
  totalSteps: number;
  visibleSteps: Readonly<Ref<ScenarioStep[]>>;
  isComplete: Readonly<Ref<boolean>>;
  stepForward: () => void;
  play: () => void;
  pause: () => void;
  reset: () => void;
  setSpeed: (speed: number) => void;
}

export function createSimulatorState(steps: ScenarioStep[]): SimulatorState {
  const currentIndex = ref(0);
  const isPlaying = ref(false);
  const speed = ref(800);
  let timer: ReturnType<typeof setInterval> | null = null;

  const visibleSteps = computed(() => steps.slice(0, currentIndex.value));
  const isComplete = computed(() => currentIndex.value >= steps.length);

  function pause() {
    isPlaying.value = false;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function stepForward() {
    if (currentIndex.value < steps.length) {
      currentIndex.value += 1;
    }
    if (currentIndex.value >= steps.length) {
      pause();
    }
  }

  function play() {
    if (isComplete.value || isPlaying.value) return;
    isPlaying.value = true;
    timer = setInterval(stepForward, speed.value);
  }

  function reset() {
    pause();
    currentIndex.value = 0;
  }

  function setSpeed(nextSpeed: number) {
    speed.value = nextSpeed;
    if (isPlaying.value) {
      pause();
      play();
    }
  }

  return {
    currentIndex,
    isPlaying,
    speed,
    totalSteps: steps.length,
    visibleSteps,
    isComplete,
    stepForward,
    play,
    pause,
    reset,
    setSpeed,
  };
}
