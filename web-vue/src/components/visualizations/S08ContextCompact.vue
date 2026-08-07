<template>
  <section class="context-compact-vis" data-testid="s08-context-compact">
    <h2>{{ title || "Three-Layer Context Compression" }}</h2>

    <div class="stage">
      <div class="context-grid">
        <div class="window-panel">
          <div class="mono-label">Context Window</div>
          <div class="context-window" :style="{ height: `${WINDOW_HEIGHT}px` }">
            <TransitionGroup name="block" tag="div" class="block-stack">
              <div
                v-for="block in state.blocks"
                :key="block.id"
                :class="blockClass(block)"
                :style="{ height: `${block.heightPx}px` }"
              >
                <span v-if="block.heightPx >= 14">{{ block.label }}</span>
              </div>
            </TransitionGroup>

            <div class="fill-line" :style="{ bottom: `${state.fillPercent}%` }">
              <span>{{ state.fillPercent }}%</span>
            </div>
          </div>

          <div class="token-display">{{ tokenDisplay }}</div>
          <div class="token-max">/ 100K</div>
        </div>

        <div class="details-panel">
          <div>
            <div class="token-row">
              <span>Token usage</span>
              <span>{{ state.tokenCount.toLocaleString() }} / {{ MAX_TOKENS.toLocaleString() }}</span>
            </div>
            <div class="budget-track">
              <div :class="['budget-fill', fillTone]" :style="{ width: `${state.fillPercent}%` }" />
            </div>
          </div>

          <div class="legend" aria-label="Message type legend">
            <div v-for="item in LEGEND_ITEMS" :key="item.label" class="legend-item">
              <span :class="['legend-swatch', item.tone]" />
              <span>{{ item.label }}</span>
            </div>
          </div>

          <div class="layer-grid">
            <article v-for="layer in COMPRESSION_LAYERS" :key="layer.full" :class="layerClass(layer)">
              <div class="layer-head">
                <span>{{ layer.label }}</span>
                <em>{{ currentStep >= layer.step ? "used" : "waiting" }}</em>
              </div>
              <div class="layer-copy">
                <div>{{ layer.trigger }}</div>
                <p>{{ layer.action }}</p>
              </div>
            </article>
          </div>

          <Transition name="fade-slide">
            <div v-if="currentStep === 2" class="tool-callout">
              <strong>tool_results are the largest blocks</strong>
              <p>File contents, command outputs, search results -- each one is thousands of tokens.</p>
            </div>
          </Transition>

          <Transition name="fade-scale">
            <div v-if="state.compressionLabel" :class="['compression-banner', compressionTone]">
              <strong>{{ state.compressionLabel }}</strong>
              <p>{{ compressionDescription }}</p>
            </div>
          </Transition>

          <Transition name="fade">
            <div v-if="currentStep === 6" class="final-summary">
              <div v-for="(layer, index) in COMPRESSION_LAYERS" :key="`summary-${layer.full}`" :class="summaryClass(layer)">
                <span>Stage {{ index + 1 }}: {{ layer.label }} -- {{ layer.action }}</span>
                <em>{{ layer.trigger }}</em>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="current.title"
        :step-description="current.description"
        @prev="prev"
        @next="next"
        @reset="reset"
        @toggle="toggleAutoPlay"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

type BlockType = "user" | "assistant" | "tool_result";
type LayerTone = "micro" | "auto" | "manual";

interface ContextBlock {
  id: string;
  type: BlockType;
  label: string;
  tokens: number;
}

interface RenderBlock {
  id: string;
  type: BlockType;
  label: string;
  heightPx: number;
  compressed?: boolean;
}

interface StepState {
  blocks: RenderBlock[];
  tokenCount: number;
  fillPercent: number;
  compressionLabel: string | null;
}

interface CompressionLayer {
  label: string;
  full: string;
  trigger: string;
  action: string;
  step: number;
  tone: LayerTone;
}

const BLOCK_LABELS: Record<BlockType, string> = {
  user: "USR",
  assistant: "AST",
  tool_result: "TRL",
};

const LEGEND_ITEMS = [
  { label: "user", tone: "tone-user" },
  { label: "assistant", tone: "tone-assistant" },
  { label: "tool_result", tone: "tone-tool" },
] as const;

const MAX_TOKENS = 100000;
const WINDOW_HEIGHT = 350;

const STEPS = [
  {
    title: "Growing Context",
    description: "The context window holds the conversation. Each API call adds more messages.",
  },
  {
    title: "Context Growing",
    description: "As the agent works, messages accumulate. The context window fills up.",
  },
  {
    title: "Approaching Limit",
    description: "Old tool_results are the biggest consumers. Micro-compact targets these first.",
  },
  {
    title: "Stage 1: Micro-Compact",
    description: "Replace old tool_results with short summaries. Automatic, transparent to the model.",
  },
  {
    title: "Still Growing",
    description: "Work continues. Context grows again toward the threshold...",
  },
  {
    title: "Stage 2: Auto-Compact",
    description: "Entire conversation summarized into a compact block. Triggered at token threshold.",
  },
  {
    title: "Stage 3: /compact",
    description: "User-triggered, most aggressive. Three layers of strategic forgetting enable infinite sessions.",
  },
] as const;

const COMPRESSION_LAYERS: CompressionLayer[] = [
  {
    label: "Micro",
    full: "MICRO-COMPACT",
    trigger: "old tool_result",
    action: "shrink bulky outputs",
    step: 3,
    tone: "micro",
  },
  {
    label: "Auto",
    full: "AUTO-COMPACT",
    trigger: "token threshold",
    action: "summarize the conversation",
    step: 5,
    tone: "auto",
  },
  {
    label: "Manual",
    full: "/compact",
    trigger: "user command",
    action: "keep one compact summary",
    step: 6,
    tone: "manual",
  },
];

defineProps<{
  title?: string;
}>();

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEPS.length,
  autoPlayInterval: 2500,
});

const current = computed(() => STEPS[currentStep.value]);
const state = computed(() => computeStepState(currentStep.value));

const tokenDisplay = computed(() => `${(state.value.tokenCount / 1000).toFixed(0)}K`);

const fillTone = computed(() => {
  if (state.value.fillPercent > 75) return "danger";
  if (state.value.fillPercent > 45) return "warning";
  return "healthy";
});

const compressionTone = computed(() => {
  if (currentStep.value === 3) return "micro";
  if (currentStep.value === 5) return "auto";
  return "manual";
});

const compressionDescription = computed(() => {
  if (currentStep.value === 3) return "Old tool_results shrunk to tiny summaries";
  if (currentStep.value === 5) return "Full conversation compressed to summary block";
  return "Most aggressive compression -- near-empty context";
});

function generateBlocks(count: number, seed: number): ContextBlock[] {
  const types: BlockType[] = ["user", "assistant", "tool_result"];
  const blocks: ContextBlock[] = [];

  for (let index = 0; index < count; index += 1) {
    const type = types[(index + seed) % types.length];
    const tokens = type === "tool_result" ? 4000 + (index % 3) * 1000 : 1500 + (index % 4) * 500;
    blocks.push({
      id: `b-${seed}-${index}`,
      type,
      label: `${BLOCK_LABELS[type]} ${index + 1}`,
      tokens,
    });
  }

  return blocks;
}

function scaleBlocks(blocks: ContextBlock[], fillRatio: number): RenderBlock[] {
  const totalRawTokens = blocks.reduce((total, block) => total + block.tokens, 0);
  return blocks.map((block) => ({
    ...block,
    heightPx: Math.max(fillRatio >= 0.75 ? 10 : 12, (block.tokens / totalRawTokens) * WINDOW_HEIGHT * fillRatio),
  }));
}

function computeStepState(step: number): StepState {
  switch (step) {
    case 0:
      return {
        blocks: scaleBlocks(generateBlocks(8, 0), 0.3).map((block) => ({
          ...block,
          heightPx: Math.max(16, block.heightPx),
        })),
        tokenCount: 30000,
        fillPercent: 30,
        compressionLabel: null,
      };
    case 1:
      return {
        blocks: scaleBlocks(generateBlocks(16, 0), 0.6),
        tokenCount: 60000,
        fillPercent: 60,
        compressionLabel: null,
      };
    case 2:
      return {
        blocks: scaleBlocks(generateBlocks(20, 0), 0.8),
        tokenCount: 80000,
        fillPercent: 80,
        compressionLabel: null,
      };
    case 3: {
      const raw = generateBlocks(20, 0);
      const totalRawTokens = raw.reduce((total, block) => total + block.tokens, 0);
      return {
        blocks: raw.map((block) => ({
          ...block,
          heightPx:
            block.type === "tool_result"
              ? 6
              : Math.max(12, (block.tokens / totalRawTokens) * WINDOW_HEIGHT * 0.6),
          compressed: block.type === "tool_result",
        })),
        tokenCount: 60000,
        fillPercent: 60,
        compressionLabel: "MICRO-COMPACT",
      };
    }
    case 4:
      return {
        blocks: scaleBlocks(generateBlocks(24, 1), 0.85),
        tokenCount: 85000,
        fillPercent: 85,
        compressionLabel: null,
      };
    case 5:
      return {
        blocks: [
          {
            id: "auto-summary",
            type: "assistant",
            label: "SUMMARY",
            heightPx: 40,
          },
          ...generateBlocks(4, 2).map((block) => ({
            ...block,
            heightPx: 20,
          })),
        ],
        tokenCount: 25000,
        fillPercent: 25,
        compressionLabel: "AUTO-COMPACT",
      };
    case 6:
      return {
        blocks: [
          {
            id: "compact-summary",
            type: "assistant",
            label: "COMPACT SUMMARY",
            heightPx: 24,
          },
        ],
        tokenCount: 8000,
        fillPercent: 8,
        compressionLabel: "/compact",
      };
    default:
      return {
        blocks: [],
        tokenCount: 0,
        fillPercent: 0,
        compressionLabel: null,
      };
  }
}

function blockClass(block: RenderBlock) {
  return [
    "context-block",
    {
      compressed: block.compressed,
      user: block.type === "user",
      assistant: block.type === "assistant",
      tool: block.type === "tool_result",
    },
  ];
}

function layerClass(layer: CompressionLayer) {
  return [
    "layer-card",
    layer.tone,
    {
      reached: currentStep.value >= layer.step,
      active: state.value.compressionLabel === layer.full,
    },
  ];
}

function summaryClass(layer: CompressionLayer) {
  return ["stage-summary", layer.tone];
}
</script>

<style scoped>
.context-compact-vis {
  min-height: 500px;
}

.context-compact-vis h2 {
  margin: 0 0 16px;
  color: #18181b;
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.stage {
  min-height: 500px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.context-grid {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 20px;
}

.window-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mono-label {
  margin-bottom: 8px;
  color: #71717a;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  font-weight: 700;
}

.context-window {
  position: relative;
  width: 96px;
  max-width: 100%;
  overflow: hidden;
  border: 2px solid #d4d4d8;
  border-radius: 12px;
  background: #fafafa;
}

.block-stack {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  flex-direction: column-reverse;
  gap: 1px;
  padding: 4px;
}

.context-block {
  display: flex;
  width: 100%;
  min-height: 4px;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  color: #ffffff;
  font-size: 8px;
  font-weight: 650;
  line-height: 1;
  overflow: hidden;
  transform-origin: bottom;
  transition:
    height 400ms ease,
    opacity 180ms ease,
    transform 180ms ease;
}

.context-block span {
  min-width: 0;
  overflow: hidden;
  padding: 0 4px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-block.user {
  background: #3b82f6;
}

.context-block.assistant {
  background: #71717a;
}

.context-block.tool {
  background: #10b981;
}

.context-block.compressed {
  background: #6ee7b7;
}

.fill-line {
  position: absolute;
  right: 0;
  left: 0;
  border-top: 2px dashed #f87171;
  transition: bottom 500ms ease;
}

.fill-line span {
  position: absolute;
  top: -18px;
  right: 4px;
  color: #ef4444;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 9px;
  font-weight: 800;
}

.token-display {
  margin-top: 8px;
  color: #3f3f46;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 14px;
  font-weight: 800;
}

.token-max {
  color: #a1a1aa;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
}

.details-panel {
  min-width: 0;
}

.token-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #71717a;
  font-size: 12px;
}

.token-row span:last-child {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  overflow-wrap: anywhere;
}

.budget-track {
  height: 12px;
  margin-top: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: #f4f4f5;
}

.budget-fill {
  height: 100%;
  border-radius: 999px;
  transition:
    width 500ms ease,
    background-color 220ms ease;
}

.budget-fill.healthy {
  background: #10b981;
}

.budget-fill.warning {
  background: #f59e0b;
}

.budget-fill.danger {
  background: #ef4444;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #71717a;
  font-size: 10px;
}

.legend-swatch {
  width: 12px;
  height: 12px;
  flex: 0 0 auto;
  border-radius: 3px;
}

.tone-user {
  background: #3b82f6;
}

.tone-assistant {
  background: #71717a;
}

.tone-tool {
  background: #10b981;
}

.layer-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 16px;
}

.layer-card {
  min-width: 0;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #fafafa;
  padding: 12px;
  color: #71717a;
  transition:
    background-color 220ms ease,
    border-color 220ms ease,
    color 220ms ease,
    transform 220ms ease;
}

.layer-card.active {
  animation: active-bob 800ms ease-in-out infinite;
}

.layer-card.micro.reached {
  border-color: #fde68a;
  background: #fffbeb;
  color: #92400e;
}

.layer-card.auto.reached {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.layer-card.manual.reached {
  border-color: #a7f3d0;
  background: #ecfdf5;
  color: #047857;
}

.layer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 14px;
  font-weight: 750;
}

.layer-head em {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.72);
  padding: 2px 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
}

.layer-copy {
  display: grid;
  gap: 4px;
  margin-top: 8px;
  font-size: 11px;
  line-height: 1.35;
}

.layer-copy div {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  overflow-wrap: anywhere;
}

.layer-copy p {
  margin: 0;
  opacity: 0.82;
  overflow-wrap: anywhere;
}

.tool-callout {
  margin-top: 12px;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  background: #fffbeb;
  padding: 8px 12px;
}

.tool-callout strong {
  display: block;
  color: #b45309;
  font-size: 12px;
  line-height: 1.35;
}

.tool-callout p {
  margin: 2px 0 0;
  color: #d97706;
  font-size: 11px;
  line-height: 1.4;
}

.compression-banner {
  margin-top: 16px;
  border: 2px solid;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.compression-banner strong {
  display: block;
  font-size: 18px;
  font-weight: 900;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.compression-banner p {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.4;
}

.compression-banner.micro {
  border-color: #fbbf24;
  background: #fffbeb;
  color: #b45309;
}

.compression-banner.auto {
  border-color: #60a5fa;
  background: #eff6ff;
  color: #2563eb;
}

.compression-banner.manual {
  border-color: #34d399;
  background: #ecfdf5;
  color: #059669;
}

.final-summary {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.stage-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  line-height: 1.35;
}

.stage-summary span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.stage-summary em {
  flex: 0 0 auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  font-style: normal;
  opacity: 0.8;
}

.stage-summary.micro {
  background: #fffbeb;
  color: #92400e;
}

.stage-summary.auto {
  background: #eff6ff;
  color: #1e40af;
}

.stage-summary.manual {
  background: #ecfdf5;
  color: #047857;
}

.block-enter-active,
.block-leave-active,
.fade-enter-active,
.fade-leave-active,
.fade-slide-enter-active,
.fade-slide-leave-active,
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.block-enter-from,
.block-leave-to {
  opacity: 0;
  transform: scaleY(0);
}

.fade-enter-from,
.fade-leave-to,
.fade-slide-enter-from,
.fade-slide-leave-to,
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  transform: translateY(8px);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  transform: scale(0.96);
}

@keyframes active-bob {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-2px);
  }
}

:deep(.step-controls) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
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
  border: 1px solid #d4d4d8;
  border-radius: 6px;
  background: #ffffff;
  padding: 6px 10px;
  color: #18181b;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

:deep(.step-buttons button:disabled) {
  color: #a1a1aa;
  cursor: not-allowed;
}

:deep(.step-progress) {
  display: flex;
  align-items: center;
  gap: 6px;
}

:deep(.step-progress span) {
  width: 18px;
  height: 4px;
  border-radius: 999px;
  background: #e4e4e7;
}

:deep(.step-progress span.done),
:deep(.step-progress span.active) {
  background: #18181b;
}

:deep(.step-progress em) {
  margin-left: 4px;
  color: #71717a;
  font-size: 11px;
  font-style: normal;
}

@media (min-width: 640px) {
  .stage {
    padding: 24px;
  }

  :deep(.step-controls) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

@media (max-width: 760px) {
  .context-grid {
    grid-template-columns: 1fr;
  }

  .layer-grid {
    grid-template-columns: 1fr;
  }

  .stage-summary {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }
}
</style>
