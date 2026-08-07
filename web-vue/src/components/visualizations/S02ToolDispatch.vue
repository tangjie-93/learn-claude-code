<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";

interface ToolDef {
  name: string;
  desc: string;
  tone: "orange" | "sky" | "emerald" | "violet";
}

interface StepInfo {
  title: string;
  desc: string;
}

defineProps<{
  title?: string;
}>();

const tools: ToolDef[] = [
  { name: "bash", desc: "Execute shell commands", tone: "orange" },
  { name: "read_file", desc: "Read file contents", tone: "sky" },
  { name: "write_file", desc: "Create or overwrite a file", tone: "emerald" },
  { name: "edit_file", desc: "Apply targeted edits", tone: "violet" },
];

const activeToolPerStep = [-1, 0, 1, 2, 3, 4];

const requestPerStep: Array<string | null> = [
  null,
  '{ name: "bash", input: { cmd: "ls -la" } }',
  '{ name: "read_file", input: { path: "src/auth.ts" } }',
  '{ name: "write_file", input: { path: "config.json" } }',
  '{ name: "edit_file", input: { path: "index.ts" } }',
  null,
];

const stepInfo: StepInfo[] = [
  { title: "The Dispatch Map", desc: "A dictionary maps tool names to handler functions. The loop code never changes." },
  { title: "Route: bash", desc: "tool_call.name -> handlers['bash'](input). Name-based routing." },
  { title: "Route: read_file", desc: "Same pattern, different handler. Validate input, execute, return result." },
  { title: "Route: write_file", desc: "Every tool returns a tool_result that goes back into messages[]." },
  { title: "Route: edit_file", desc: "Adding a new tool = adding one entry to the dispatch map." },
  { title: "The Key Insight", desc: "The while loop stays the same. You only grow the dispatch map. That's it." },
];

const svgWidth = 600;
const svgHeight = 320;
const dispatcherX = svgWidth / 2;
const dispatcherY = 60;
const dispatcherW = 160;
const dispatcherH = 50;
const cardY = 230;
const cardW = 110;
const cardH = 65;
const cardGap = 20;

const {
  currentStep,
  totalSteps,
  next,
  prev,
  reset,
  isPlaying,
  toggleAutoPlay,
  isFirstStep,
  isLastStep,
} = useSteppedVisualization({ totalSteps: 6, autoPlayInterval: 2500 });

const activeToolIdx = computed(() => activeToolPerStep[currentStep.value]);
const request = computed(() => requestPerStep[currentStep.value]);
const currentStepInfo = computed(() => stepInfo[currentStep.value]);
const isAllActive = computed(() => activeToolIdx.value === 4);

function getCardX(index: number): number {
  const totalWidth = tools.length * cardW + (tools.length - 1) * cardGap;
  const startX = (svgWidth - totalWidth) / 2;
  return startX + index * (cardW + cardGap) + cardW / 2;
}

function isToolActive(index: number): boolean {
  return isAllActive.value || index === activeToolIdx.value;
}
</script>

<template>
  <section class="tool-dispatch" data-testid="s02-tool-dispatch">
    <h2>{{ title || "Tool Dispatch Map" }}</h2>

    <div class="panel">
      <div class="incoming-row">
        <span class="incoming-label">Incoming:</span>
        <Transition name="request-fade" mode="out-in">
          <code v-if="request" :key="request" class="incoming-code">{{ request }}</code>
          <span v-else-if="currentStep === 0" key="waiting" class="waiting">waiting for tool_call...</span>
          <span v-else key="all-routes" class="all-routes">All routes active</span>
        </Transition>
      </div>

      <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="dispatch-diagram" role="img" aria-label="Tool dispatch map">
        <defs>
          <filter id="s02-dispatch-glow">
            <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#3b82f6" flood-opacity="0.6" />
          </filter>
          <filter v-for="tool in tools" :id="`s02-card-glow-${tool.tone}`" :key="`glow-${tool.name}`">
            <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="currentColor" flood-opacity="0.6" />
          </filter>
          <marker id="s02-dispatch-arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#3b82f6" />
          </marker>
          <marker id="s02-dispatch-arrow-dim" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
          </marker>
        </defs>

        <rect
          class="dispatcher-box"
          :class="{ 'is-active': currentStep > 0 }"
          :x="dispatcherX - dispatcherW / 2"
          :y="dispatcherY - dispatcherH / 2"
          :width="dispatcherW"
          :height="dispatcherH"
          rx="10"
          :filter="currentStep > 0 ? 'url(#s02-dispatch-glow)' : undefined"
        />
        <text class="dispatcher-text" :class="{ 'is-active': currentStep > 0 }" :x="dispatcherX" :y="dispatcherY + 1">
          dispatch(name)
        </text>

        <line
          v-for="(tool, index) in tools"
          :key="`line-${tool.name}`"
          class="dispatch-line"
          :class="{ 'is-active': isToolActive(index) }"
          :x1="dispatcherX"
          :y1="dispatcherY + dispatcherH / 2"
          :x2="getCardX(index)"
          :y2="cardY - cardH / 2"
          :marker-end="isToolActive(index) ? 'url(#s02-dispatch-arrow)' : 'url(#s02-dispatch-arrow-dim)'"
        />

        <g
          v-for="(tool, index) in tools"
          :key="tool.name"
          class="tool-node"
          :class="[`tool-${tool.tone}`, { 'is-active': isToolActive(index) }]"
          :data-tool="tool.name"
        >
          <rect
            class="tool-card"
            :x="getCardX(index) - cardW / 2"
            :y="cardY - cardH / 2"
            :width="cardW"
            :height="cardH"
            rx="8"
            :filter="isToolActive(index) ? `url(#s02-card-glow-${tool.tone})` : undefined"
          />
          <text class="tool-name" :x="getCardX(index)" :y="cardY - 8">{{ tool.name }}</text>
          <text class="tool-desc" :x="getCardX(index)" :y="cardY + 12">{{ tool.desc }}</text>
        </g>

        <g v-if="isAllActive" class="extensibility-indicator">
          <circle :cx="getCardX(3) + cardW / 2 + 30" :cy="cardY" r="16" />
          <text :x="getCardX(3) + cardW / 2 + 30" :y="cardY + 1">+</text>
        </g>
      </svg>

      <div class="code-strip">
        <code>
          <span class="keyword">const</span>
          handlers = {
          <span
            v-for="(tool, index) in tools"
            :key="`handler-${tool.name}`"
            class="handler-name"
            :class="{ 'is-active': isToolActive(index) }"
          > {{ tool.name }},</span>
          }
        </code>
      </div>
    </div>

    <div class="step-controls">
      <div class="step-copy">
        <p class="step-title">{{ currentStepInfo.title }}</p>
        <p class="step-desc">{{ currentStepInfo.desc }}</p>
      </div>
      <div class="button-row">
        <button type="button" :disabled="isFirstStep" data-testid="step-prev" @click="prev">Prev</button>
        <button type="button" data-testid="step-play" @click="toggleAutoPlay">{{ isPlaying ? "Pause" : "Play" }}</button>
        <button type="button" data-testid="step-reset" @click="reset">Reset</button>
        <button type="button" :disabled="isLastStep" data-testid="step-next" @click="next">Next</button>
      </div>
      <div class="step-meter" aria-label="Step progress">
        <span
          v-for="step in totalSteps"
          :key="step"
          class="step-dot"
          :class="{ 'is-active': step - 1 === currentStep }"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.tool-dispatch {
  min-height: 500px;
  display: grid;
  gap: 16px;
  color: #18181b;
}

.tool-dispatch h2 {
  margin: 0;
  font-size: 20px;
  line-height: 1.3;
  font-weight: 650;
}

.panel {
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.incoming-row {
  min-height: 32px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.incoming-label {
  flex: 0 0 auto;
  color: #71717a;
  font-size: 12px;
  font-weight: 600;
}

.incoming-code {
  border-radius: 6px;
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  font-weight: 650;
}

.waiting {
  color: #a1a1aa;
  font-size: 12px;
}

.all-routes {
  color: #059669;
  font-size: 12px;
  font-weight: 650;
}

.request-fade-enter-active,
.request-fade-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

.request-fade-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}

.request-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.dispatch-diagram {
  width: 100%;
  min-height: 240px;
  display: block;
  border: 1px solid #f4f4f5;
  border-radius: 6px;
  background: #fafafa;
}

.dispatcher-box,
.tool-card,
.dispatch-line,
.dispatcher-text,
.tool-name,
.tool-desc {
  transition: fill 240ms ease, stroke 240ms ease, stroke-width 240ms ease, opacity 240ms ease;
}

.dispatcher-box {
  fill: #ffffff;
  stroke: #94a3b8;
  stroke-width: 2;
}

.dispatcher-box.is-active {
  fill: #dbeafe;
  stroke: #3b82f6;
}

.dispatcher-text,
.tool-name,
.tool-desc,
.extensibility-indicator text {
  text-anchor: middle;
  dominant-baseline: middle;
}

.dispatcher-text {
  fill: #18181b;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 13px;
  font-weight: 700;
}

.dispatcher-text.is-active {
  fill: #1e40af;
}

.dispatch-line {
  stroke: #cbd5e1;
  stroke-width: 1.5;
}

.dispatch-line.is-active {
  stroke: #3b82f6;
  stroke-width: 2.5;
}

.tool-card {
  fill: #ffffff;
  stroke: #94a3b8;
  stroke-width: 2;
}

.tool-name {
  fill: #18181b;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 700;
}

.tool-desc {
  fill: #71717a;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 8px;
}

.tool-node.is-active .tool-name {
  fill: #ffffff;
}

.tool-node.is-active .tool-desc {
  fill: rgba(255, 255, 255, 0.82);
}

.tool-orange {
  color: #f97316;
}

.tool-sky {
  color: #0ea5e9;
}

.tool-emerald {
  color: #10b981;
}

.tool-violet {
  color: #8b5cf6;
}

.tool-orange.is-active .tool-card {
  fill: #f97316;
  stroke: #ea580c;
}

.tool-sky.is-active .tool-card {
  fill: #0ea5e9;
  stroke: #0284c7;
}

.tool-emerald.is-active .tool-card {
  fill: #10b981;
  stroke: #059669;
}

.tool-violet.is-active .tool-card {
  fill: #8b5cf6;
  stroke: #7c3aed;
}

.extensibility-indicator {
  animation: pop-in 220ms ease-out;
}

.extensibility-indicator circle {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 2;
  stroke-dasharray: 4 3;
}

.extensibility-indicator text {
  fill: #3b82f6;
  font-size: 18px;
  font-weight: 700;
}

.code-strip {
  margin-top: 12px;
  border-radius: 6px;
  background: #f4f4f5;
  padding: 8px 12px;
}

.code-strip code {
  color: #52525b;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  line-height: 1.6;
}

.keyword,
.handler-name.is-active {
  color: #2563eb;
  font-weight: 700;
}

.step-controls {
  display: grid;
  gap: 12px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  padding: 14px 16px;
}

.step-title {
  margin: 0;
  color: #18181b;
  font-size: 14px;
  font-weight: 700;
}

.step-desc {
  margin: 4px 0 0;
  color: #52525b;
  font-size: 13px;
  line-height: 1.45;
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.button-row button {
  border: 1px solid #d4d4d8;
  border-radius: 6px;
  background: #ffffff;
  color: #27272a;
  min-width: 68px;
  padding: 6px 10px;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
}

.button-row button:hover:not(:disabled) {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.button-row button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.step-meter {
  display: flex;
  gap: 6px;
}

.step-dot {
  width: 28px;
  height: 4px;
  border-radius: 999px;
  background: #d4d4d8;
  transition: background 180ms ease;
}

.step-dot.is-active {
  background: #3b82f6;
}

@keyframes pop-in {
  from {
    opacity: 0;
    transform: scale(0.75);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

:global(.dark) .tool-dispatch {
  color: #f4f4f5;
}

:global(.dark) .tool-dispatch h2 {
  color: #f4f4f5;
}

:global(.dark) .panel,
:global(.dark) .step-controls {
  border-color: #3f3f46;
  background: #18181b;
}

:global(.dark) .incoming-label {
  color: #a1a1aa;
}

:global(.dark) .incoming-code {
  background: rgba(30, 58, 138, 0.55);
  color: #93c5fd;
}

:global(.dark) .waiting {
  color: #52525b;
}

:global(.dark) .all-routes {
  color: #34d399;
}

:global(.dark) .dispatch-diagram {
  border-color: #27272a;
  background: #09090b;
}

:global(.dark) .dispatcher-box,
:global(.dark) .tool-card {
  fill: rgba(39, 39, 42, 0.7);
  stroke: #3f3f46;
}

:global(.dark) .dispatcher-box.is-active {
  fill: rgba(30, 58, 138, 0.6);
  stroke: #3b82f6;
}

:global(.dark) .dispatcher-text,
:global(.dark) .tool-name {
  fill: #f4f4f5;
}

:global(.dark) .dispatcher-text.is-active {
  fill: #bfdbfe;
}

:global(.dark) .tool-desc {
  fill: #a1a1aa;
}

:global(.dark) .dispatch-line {
  stroke: #3f3f46;
}

:global(.dark) .dispatch-line.is-active {
  stroke: #3b82f6;
}

:global(.dark) .code-strip {
  background: #27272a;
}

:global(.dark) .code-strip code {
  color: #d4d4d8;
}

:global(.dark) .step-title {
  color: #f4f4f5;
}

:global(.dark) .step-desc {
  color: #d4d4d8;
}

:global(.dark) .button-row button {
  border-color: #3f3f46;
  background: #18181b;
  color: #f4f4f5;
}

:global(.dark) .button-row button:hover:not(:disabled) {
  border-color: #60a5fa;
  background: rgba(30, 58, 138, 0.35);
  color: #bfdbfe;
}

:global(.dark) .step-dot {
  background: #52525b;
}

:global(.dark) .step-dot.is-active {
  background: #60a5fa;
}
</style>
