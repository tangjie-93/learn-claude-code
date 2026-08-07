<template>
  <section class="background-vis" data-testid="s13-background-tasks">
    <h2>{{ title || "Background Task Lanes" }}</h2>

    <div class="background-panel">
      <svg viewBox="0 0 780 380" class="timeline-svg" aria-label="Background task lanes">
        <defs>
          <marker
            id="s13-fork-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-fill" />
          </marker>
          <marker
            id="s13-drain-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
          </marker>
          <filter id="s13-block-glow" x="-10%" y="-20%" width="120%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feFlood flood-color="#8b5cf6" flood-opacity="0.2" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <line
          :x1="TIMELINE_LEFT"
          y1="30"
          :x2="TIMELINE_RIGHT"
          y2="30"
          class="axis-line"
          stroke-dasharray="4 3"
        />
        <text :x="TIMELINE_LEFT" y="22" class="mono-label">t=0</text>
        <text :x="TIMELINE_RIGHT" y="22" text-anchor="end" class="mono-label">time</text>

        <g v-for="lane in lanes" :key="lane.key">
          <rect
            :x="TIMELINE_LEFT"
            :y="lane.y"
            :width="TIMELINE_WIDTH"
            :height="LANE_HEIGHT"
            rx="6"
            class="lane-rect"
          />
          <line
            :x1="TIMELINE_LEFT"
            :y1="lane.y + LANE_HEIGHT / 2"
            :x2="TIMELINE_RIGHT"
            :y2="lane.y + LANE_HEIGHT / 2"
            class="lane-guide"
            stroke-dasharray="4 2"
          />
          <text
            :x="TIMELINE_LEFT - 10"
            :y="lane.y + LANE_HEIGHT / 2 + 1"
            text-anchor="end"
            dominant-baseline="middle"
            class="lane-label"
          >
            {{ lane.label }}
          </text>
        </g>

        <g v-for="block in visibleBlocks" :key="`${block.lane}-block`" class="work-block">
          <rect
            :x="fractionToX(block.startFraction)"
            :y="LANE_Y[block.lane] + 4"
            :width="blockWidth(block)"
            :height="LANE_HEIGHT - 8"
            rx="5"
            :fill="block.color"
            :class="{ complete: isBlockComplete(block) }"
            :filter="!isBlockComplete(block) && block.lane === 'main' ? 'url(#s13-block-glow)' : undefined"
          />
          <text
            v-if="blockWidth(block) > 60 && block.label"
            :x="fractionToX(block.startFraction) + blockWidth(block) / 2"
            :y="LANE_Y[block.lane] + LANE_HEIGHT / 2 + 1"
            text-anchor="middle"
            dominant-baseline="middle"
            class="block-label"
          >
            {{ block.label }}
          </text>
          <text
            v-if="isBlockComplete(block)"
            :x="fractionToX(getBlockEndFraction(block, currentStep)) + 6"
            :y="LANE_Y[block.lane] + LANE_HEIGHT / 2 + 1"
            dominant-baseline="middle"
            class="done-label"
          >
            done
          </text>
        </g>

        <line
          v-for="arrow in visibleForkArrows"
          :key="`fork-${arrow.toLane}`"
          :x1="fractionToX(arrow.fromFraction)"
          :y1="LANE_Y.main + LANE_HEIGHT"
          :x2="fractionToX(arrow.fromFraction) + 20"
          :y2="LANE_Y[arrow.toLane]"
          class="fork-line"
          marker-end="url(#s13-fork-arrow)"
        />

        <g v-if="showLlmMarker" class="llm-marker">
          <line
            :x1="fractionToX(LLM_CALL_FRACTION)"
            :y1="LANE_Y.main"
            :x2="fractionToX(LLM_CALL_FRACTION)"
            :y2="LANE_Y.main + LANE_HEIGHT"
            stroke-dasharray="3 2"
          />
          <rect :x="fractionToX(LLM_CALL_FRACTION) - 36" :y="LANE_Y.main - 16" width="72" height="16" rx="3" />
          <text
            :x="fractionToX(LLM_CALL_FRACTION)"
            :y="LANE_Y.main - 6"
            text-anchor="middle"
            dominant-baseline="middle"
          >
            LLM API call
          </text>
        </g>

        <rect :x="TIMELINE_LEFT" :y="QUEUE_Y" :width="TIMELINE_WIDTH" height="54" rx="8" class="queue-rect" />
        <text :x="TIMELINE_LEFT - 10" :y="QUEUE_Y + 18" text-anchor="end" class="queue-label">Notification</text>
        <text :x="TIMELINE_LEFT - 10" :y="QUEUE_Y + 32" text-anchor="end" class="queue-label">Queue</text>

        <g v-for="(card, index) in visibleQueueCards" :key="card.id" :transform="queueCardTransform(card, index)" class="queue-card">
          <rect width="130" height="34" rx="5" :class="{ draining: isCardDraining(card) }" />
          <text x="65" y="13" text-anchor="middle" dominant-baseline="middle" class="queue-card-type">tool_result</text>
          <text x="65" y="26" text-anchor="middle" dominant-baseline="middle" class="queue-card-label">
            {{ card.label }}
          </text>
        </g>

        <g v-if="currentStep >= 6" class="drain-flow">
          <line
            :x1="fractionToX(LLM_CALL_FRACTION) + 20"
            :y1="QUEUE_Y"
            :x2="fractionToX(LLM_CALL_FRACTION) + 20"
            :y2="LANE_Y.main + LANE_HEIGHT + 4"
            marker-end="url(#s13-drain-arrow)"
          />
        </g>
        <text
          v-if="currentStep >= 6"
          :x="TIMELINE_LEFT + TIMELINE_WIDTH / 2"
          :y="QUEUE_Y + 30"
          text-anchor="middle"
          dominant-baseline="middle"
          class="drained-label"
        >
          queue drained -- injected into next LLM call
        </text>
      </svg>

      <div class="legend" aria-label="Background task legend">
        <span v-for="item in legendItems" :key="item.label" class="legend-item">
          <span class="legend-swatch" :style="{ background: item.color }" />
          {{ item.label }}
        </span>
      </div>
    </div>

    <StepControls
      :current-step="currentStep"
      :total-steps="totalSteps"
      :is-playing="isPlaying"
      :step-title="stepInfo.title"
      :step-description="stepInfo.description"
      @reset="reset"
      @prev="prev"
      @toggle="toggleAutoPlay"
      @next="next"
    />
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

defineProps<{ title?: string }>();

interface StepInfo {
  title: string;
  description: string;
}

type LaneKey = "main" | "bg1" | "bg2";

interface WorkBlock {
  lane: LaneKey;
  startFraction: number;
  endFraction: number;
  color: string;
  label?: string;
  appearsAtStep: number;
  completesAtStep?: number;
}

interface ForkArrow {
  fromFraction: number;
  toLane: Exclude<LaneKey, "main">;
  appearsAtStep: number;
}

interface QueueCard {
  id: string;
  label: string;
  appearsAtStep: number;
  drainsAtStep: number;
}

const STEP_INFO: StepInfo[] = [
  {
    title: "Three Lanes",
    description: "The agent has a main thread and can spawn daemon background threads for parallel work.",
  },
  {
    title: "Main Thread Working",
    description: "The main agent loop runs as usual, processing user requests.",
  },
  {
    title: "Spawn Background",
    description: "Background tasks run as daemon threads. The main loop doesn't wait for them.",
  },
  {
    title: "Multiple Backgrounds",
    description: "Multiple background tasks can run concurrently.",
  },
  {
    title: "Task Completes",
    description: "Background task finishes. Its result goes to the notification queue.",
  },
  {
    title: "Queue Fills",
    description: "Results accumulate in the queue, invisible to the model during this turn.",
  },
  {
    title: "Drain Queue",
    description:
      "Just before the next LLM call, all queued notifications are injected as tool_results. Non-blocking, async.",
  },
];

const LANE_Y = {
  main: 60,
  bg1: 140,
  bg2: 220,
} as const;

const LANE_HEIGHT = 44;
const TIMELINE_LEFT = 160;
const TIMELINE_RIGHT = 720;
const TIMELINE_WIDTH = TIMELINE_RIGHT - TIMELINE_LEFT;
const QUEUE_Y = 300;
const LLM_CALL_FRACTION = 0.82;

const WORK_BLOCKS: WorkBlock[] = [
  {
    lane: "main",
    startFraction: 0,
    endFraction: 1,
    color: "#8b5cf6",
    label: "Main agent loop",
    appearsAtStep: 1,
  },
  {
    lane: "bg1",
    startFraction: 0.18,
    endFraction: 0.75,
    color: "#10b981",
    label: "Run tests",
    appearsAtStep: 2,
    completesAtStep: 5,
  },
  {
    lane: "bg2",
    startFraction: 0.35,
    endFraction: 0.58,
    color: "#3b82f6",
    label: "Lint code",
    appearsAtStep: 3,
    completesAtStep: 4,
  },
];

const FORK_ARROWS: ForkArrow[] = [
  { fromFraction: 0.18, toLane: "bg1", appearsAtStep: 2 },
  { fromFraction: 0.35, toLane: "bg2", appearsAtStep: 3 },
];

const QUEUE_CARDS: QueueCard[] = [
  {
    id: "lint-result",
    label: "Lint: 0 errors",
    appearsAtStep: 4,
    drainsAtStep: 6,
  },
  {
    id: "test-result",
    label: "Tests: 42 passed",
    appearsAtStep: 5,
    drainsAtStep: 6,
  },
];

const lanes = [
  { key: "main", y: LANE_Y.main, label: "Main Thread" },
  { key: "bg1", y: LANE_Y.bg1, label: "Background 1" },
  { key: "bg2", y: LANE_Y.bg2, label: "Background 2" },
] as const;

const legendItems = [
  { label: "Main thread", color: "#8b5cf6" },
  { label: "Background 1", color: "#10b981" },
  { label: "Background 2", color: "#3b82f6" },
  { label: "LLM boundary", color: "#f59e0b" },
] as const;

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEP_INFO.length,
  autoPlayInterval: 2500,
});

const stepInfo = computed(() => STEP_INFO[currentStep.value]);
const showLlmMarker = computed(() => currentStep.value >= 5);
const visibleBlocks = computed(() => WORK_BLOCKS.filter((block) => currentStep.value >= block.appearsAtStep));
const visibleForkArrows = computed(() => FORK_ARROWS.filter((arrow) => currentStep.value >= arrow.appearsAtStep));
const visibleQueueCards = computed(() => QUEUE_CARDS.filter((card) => currentStep.value >= card.appearsAtStep));

function fractionToX(fraction: number): number {
  return TIMELINE_LEFT + fraction * TIMELINE_WIDTH;
}

function getBlockEndFraction(block: WorkBlock, step: number): number {
  if (step < block.appearsAtStep) return block.startFraction;
  if (block.completesAtStep !== undefined && step >= block.completesAtStep) return block.endFraction;

  const growthSteps = (block.completesAtStep ?? 6) - block.appearsAtStep;
  const stepsElapsed = step - block.appearsAtStep;
  const progress = Math.min(stepsElapsed / growthSteps, 1);
  const range = block.endFraction - block.startFraction;
  return block.startFraction + range * progress;
}

function blockWidth(block: WorkBlock): number {
  const startX = fractionToX(block.startFraction);
  const endX = fractionToX(getBlockEndFraction(block, currentStep.value));
  return Math.max(endX - startX, 4);
}

function isBlockComplete(block: WorkBlock): boolean {
  return block.completesAtStep !== undefined && currentStep.value >= block.completesAtStep;
}

function isCardDraining(card: QueueCard): boolean {
  return currentStep.value >= card.drainsAtStep;
}

function queueCardTransform(card: QueueCard, index: number): string {
  const cardX = TIMELINE_LEFT + 20 + index * 150;
  const cardY = QUEUE_Y + 10;

  if (!isCardDraining(card)) {
    return `translate(${cardX} ${cardY})`;
  }

  const drainTargetX = fractionToX(LLM_CALL_FRACTION) + 10 + index * 15;
  const drainTargetY = LANE_Y.main + LANE_HEIGHT / 2 - 12;
  return `translate(${drainTargetX} ${drainTargetY})`;
}
</script>

<style scoped>
.background-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.background-vis h2 {
  margin: 0;
  color: var(--text);
  font-size: 20px;
  font-weight: 650;
}

.background-panel {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.timeline-svg {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}

.axis-line,
.lane-guide {
  stroke: var(--muted);
  stroke-width: 1;
  opacity: 0.55;
}

.lane-rect,
.queue-rect {
  fill: none;
  stroke: var(--border);
  stroke-width: 1;
}

.lane-label,
.queue-label {
  fill: var(--text);
  font-size: 11px;
  font-weight: 650;
}

.mono-label,
.drained-label {
  fill: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 9px;
}

.work-block rect {
  transition: width 0.6s ease, opacity 0.3s ease;
}

.work-block rect.complete {
  opacity: 0.7;
}

.block-label {
  fill: #ffffff;
  font-size: 10px;
  font-weight: 550;
  pointer-events: none;
}

.done-label {
  fill: #10b981;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 9px;
}

.fork-line {
  stroke: var(--muted);
  stroke-width: 1.5;
}

.arrow-fill {
  fill: var(--muted);
}

.llm-marker {
  opacity: 1;
}

.llm-marker line {
  stroke: #f59e0b;
  stroke-width: 2;
}

.llm-marker rect {
  fill: #f59e0b;
}

.llm-marker text {
  fill: #ffffff;
  font-size: 8px;
  font-weight: 650;
}

.queue-card {
  transition: transform 0.65s ease, opacity 0.4s ease;
}

.queue-card rect {
  fill: #d1fae5;
  stroke: #10b981;
  stroke-width: 1;
}

.queue-card rect.draining {
  fill: #fef3c7;
  stroke: #f59e0b;
}

.queue-card-type {
  fill: #047857;
  font-size: 9px;
  font-weight: 650;
}

.queue-card-label {
  fill: #065f46;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 8px;
}

.queue-card:has(rect.draining) .queue-card-type {
  fill: #b45309;
}

.queue-card:has(rect.draining) .queue-card-label {
  fill: #92400e;
}

.drain-flow line {
  stroke: #f59e0b;
  stroke-width: 1.5;
}

.drained-label {
  font-size: 10px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 16px;
  margin-top: 12px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 10px;
}

.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

:global(.dark) .queue-card rect {
  fill: rgba(6, 64, 39, 0.35);
}

:global(.dark) .queue-card rect.draining {
  fill: rgba(69, 26, 3, 0.35);
}

:global(.dark) .queue-card-type {
  fill: #34d399;
}

:global(.dark) .queue-card-label {
  fill: #10b981;
}

:global(.dark) .queue-card:has(rect.draining) .queue-card-type {
  fill: #fbbf24;
}

:global(.dark) .queue-card:has(rect.draining) .queue-card-label {
  fill: #f59e0b;
}

@media (max-width: 640px) {
  .background-panel {
    padding: 12px;
  }

  .legend {
    gap: 8px 12px;
  }
}
</style>
