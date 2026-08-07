<template>
  <section class="session-viz" data-testid="session-visualization">
    <h2>{{ title || "The Agent While-Loop" }}</h2>
    <div class="viz-card agent-loop-viz">
      <div class="viz-diagram">
        <div class="viz-code-label">while (tool_calls.length)</div>
        <svg viewBox="0 0 500 440" role="img" aria-label="Agent loop flow">
          <defs>
            <marker id="agent-loop-arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="currentColor" />
            </marker>
          </defs>
          <g v-for="edge in edges" :key="`${edge.from}->${edge.to}`">
            <path
              :d="edge.path"
              :class="{ active: activeEdges.has(`${edge.from}->${edge.to}`) }"
              marker-end="url(#agent-loop-arrow)"
            />
            <text v-if="edge.label" :x="edge.labelX" :y="edge.labelY">{{ edge.label }}</text>
          </g>
          <g v-for="node in nodes" :key="node.id" :class="{ active: activeNodes.has(node.id) }">
            <polygon v-if="node.type === 'diamond'" :points="diamondPoints(node)" />
            <rect v-else :x="node.x - node.w / 2" :y="node.y - node.h / 2" :width="node.w" :height="node.h" rx="8" />
            <text :x="node.x" :y="node.y">{{ node.label }}</text>
          </g>
        </svg>
      </div>
      <aside class="viz-side">
        <div class="message-stack">
          <div v-for="message in visibleMessages" :key="`${message.role}-${message.detail}`" :class="['message-pill', message.kind]">
            <strong>{{ message.role }}</strong>
            <span>{{ message.detail }}</span>
          </div>
          <div v-if="!visibleMessages.length" class="empty-messages">messages[]</div>
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
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

defineProps<{ title?: string }>();

const nodes = [
  { id: "start", label: "Start", x: 160, y: 30, w: 120, h: 40, type: "rect" },
  { id: "api_call", label: "API Call", x: 160, y: 110, w: 120, h: 40, type: "rect" },
  { id: "check", label: "tool_calls?", x: 160, y: 200, w: 140, h: 54, type: "diamond" },
  { id: "execute", label: "Execute Tool", x: 160, y: 300, w: 122, h: 40, type: "rect" },
  { id: "append", label: "Append Result", x: 160, y: 380, w: 124, h: 40, type: "rect" },
  { id: "end", label: "Done", x: 380, y: 200, w: 120, h: 40, type: "rect" },
] as const;

const edges = [
  { from: "start", to: "api_call", path: "M 160 50 L 160 90" },
  { from: "api_call", to: "check", path: "M 160 130 L 160 173" },
  { from: "check", to: "execute", label: "yes", labelX: 206, labelY: 256, path: "M 160 227 L 160 280" },
  { from: "execute", to: "append", path: "M 160 320 L 160 360" },
  { from: "append", to: "api_call", path: "M 98 380 L 48 380 L 48 110 L 100 110" },
  { from: "check", to: "end", label: "no", labelX: 270, labelY: 190, path: "M 230 200 L 320 200" },
];

const activeNodesPerStep = [
  [],
  ["start"],
  ["api_call"],
  ["check", "execute"],
  ["execute", "append"],
  ["api_call", "check", "execute", "append"],
  ["check", "end"],
];

const activeEdgesPerStep = [
  [],
  ["start->api_call"],
  ["api_call->check"],
  ["api_call->check", "check->execute"],
  ["execute->append"],
  ["append->api_call", "api_call->check", "check->execute", "execute->append"],
  ["api_call->check", "check->end"],
];

const messagesPerStep = [
  [],
  [{ role: "user", detail: "Fix the login bug", kind: "user" }],
  [],
  [{ role: "assistant", detail: "function_call: read_file", kind: "assistant" }],
  [{ role: "function_call_output", detail: "auth.ts contents...", kind: "tool" }],
  [
    { role: "assistant", detail: "function_call: edit_file", kind: "assistant" },
    { role: "function_call_output", detail: "file updated", kind: "tool" },
  ],
  [{ role: "assistant", detail: "final answer", kind: "final" }],
];

const stepInfoList = [
  { title: "The While Loop", description: "Every agent is a while loop that keeps calling the model until it stops." },
  { title: "User Input", description: "The loop starts when the user sends a message." },
  { title: "Call the Model", description: "Send all messages to the LLM. It decides whether to call tools." },
  { title: "Function Call", description: "The model asks for a tool. The loop continues." },
  { title: "Execute & Append", description: "Run the tool and append function_call_output to messages[]." },
  { title: "Loop Again", description: "Same code path, second iteration. The model can keep acting." },
  { title: "Done", description: "No function calls remain. The loop returns the final response." },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: stepInfoList.length,
  autoPlayInterval: 2500,
});

const activeNodes = computed(() => new Set(activeNodesPerStep[currentStep.value]));
const activeEdges = computed(() => new Set(activeEdgesPerStep[currentStep.value]));
const stepInfo = computed(() => stepInfoList[currentStep.value]);
const visibleMessages = computed(() => messagesPerStep.slice(0, currentStep.value + 1).flat());

function diamondPoints(node: (typeof nodes)[number]) {
  const halfW = node.w / 2;
  const halfH = node.h / 2;
  return `${node.x},${node.y - halfH} ${node.x + halfW},${node.y} ${node.x},${node.y + halfH} ${node.x - halfW},${node.y}`;
}
</script>
