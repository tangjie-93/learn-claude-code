<template>
  <section class="mcp-vis" data-testid="s19-mcp-tools">
    <h2>{{ title || "MCP Tool Bridge" }}</h2>
    <div class="mcp-panel">
      <div class="mcp-grid">
        <article :class="['shelf', { active: current.active === 'need' }]">
          <div class="shelf-head">
            <span class="shelf-icon">W</span>
            <h3>Built-in belt</h3>
          </div>
          <div class="chip-list">
            <code v-for="tool in builtIns" :key="tool" class="tool-chip">{{ tool }}</code>
            <div class="empty-chip">limited to local skills</div>
          </div>
        </article>

        <div class="mcp-middle">
          <article :class="['shelf', { active: current.active === 'server' || current.active === 'discover' }]">
            <div class="shelf-head">
              <span class="shelf-icon">S</span>
              <h3>External toolbox</h3>
            </div>
            <div class="server-row">
              <code>docs-server</code>
              <span :class="['status-pill', { connected }]">{{ connected ? "connected" : "offline" }}</span>
            </div>
            <div class="tool-grid">
              <code
                v-for="tool in discoveredTools"
                :key="tool.raw"
                class="tool-chip external"
              >
                {{ tool.raw }}
              </code>
              <div v-if="!discovered" class="empty-chip wide">schemas hidden until connected</div>
            </div>
          </article>

          <article :class="['shelf', { active: current.active === 'belt' || current.active === 'call' }]">
            <div class="shelf-head">
              <span class="shelf-icon">P</span>
              <h3>Agent workbench</h3>
            </div>
            <div class="tool-grid">
              <code
                v-for="tool in beltTools"
                :key="tool.namespaced"
                :class="['tool-chip', { selected: called && tool.raw === 'search' }]"
              >
                {{ tool.namespaced }}
              </code>
              <div v-if="!namespaced" class="empty-chip wide">no MCP tools on the belt</div>
            </div>
          </article>
        </div>

        <article :class="['shelf', { active: current.active === 'call' || current.active === 'result' }]">
          <div class="shelf-head">
            <span class="shelf-icon">C</span>
            <h3>Call notebook</h3>
          </div>
          <div class="call-stack">
            <code :class="['call-card', { sending: called && !returned }]">
              {{ called ? "mcp__docs__search({ query })" : "waiting for a tool call" }}
            </code>
            <div v-if="returned" class="result-card">tool_result: 3 relevant docs found</div>
          </div>
        </article>
      </div>

      <StepControls
        :current-step="currentStep"
        :total-steps="totalSteps"
        :is-playing="isPlaying"
        :step-title="current.title"
        :step-description="current.desc"
        @reset="reset"
        @prev="prev"
        @toggle="toggleAutoPlay"
        @next="next"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSteppedVisualization } from "@/composables/stepped-visualization";
import StepControls from "./StepControls.vue";

defineProps<{ title?: string }>();

const steps = [
  { title: "Need a New Tool", desc: "The agent starts with built-in tools, then notices this task needs an outside capability.", active: "need" },
  { title: "Plug In a Server", desc: "MCP is easiest to picture as plugging a named toolbox into the agent workbench.", active: "server" },
  { title: "Read the Tool Labels", desc: "The server advertises schemas, so the agent can see what each tool expects.", active: "discover" },
  { title: "Name the Tools Clearly", desc: "Each external tool gets a namespaced label, which avoids collisions with built-ins.", active: "belt" },
  { title: "Use It Like Any Tool", desc: "Once on the tool belt, the MCP tool follows the same call-and-result rhythm.", active: "call" },
  { title: "Result Comes Back", desc: "The returned data is just another tool result for the next model turn.", active: "result" },
] as const;

const builtIns = ["read_file", "edit_file", "bash"];
const serverTools = [
  { raw: "search", namespaced: "mcp__docs__search" },
  { raw: "fetch", namespaced: "mcp__docs__fetch" },
  { raw: "list_sections", namespaced: "mcp__docs__list_sections" },
];

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: steps.length,
  autoPlayInterval: 2500,
});

const current = computed(() => steps[currentStep.value]);
const connected = computed(() => currentStep.value >= 1);
const discovered = computed(() => currentStep.value >= 2);
const namespaced = computed(() => currentStep.value >= 3);
const called = computed(() => currentStep.value >= 4);
const returned = computed(() => currentStep.value >= 5);
const discoveredTools = computed(() => (discovered.value ? serverTools : []));
const beltTools = computed(() => (namespaced.value ? serverTools.slice(0, 2) : []));
</script>

<style scoped>
.mcp-vis {
  min-height: 500px;
  display: grid;
  gap: 16px;
}

.mcp-vis h2,
.shelf h3 {
  margin: 0;
}

.mcp-panel {
  display: grid;
  gap: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 16px;
}

.mcp-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 14px;
}

.mcp-middle,
.chip-list,
.call-stack {
  display: grid;
  gap: 10px;
}

.shelf {
  display: grid;
  align-content: start;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 12px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.shelf.active {
  border-color: #10b981;
  background: #ecfdf5;
}

.shelf-head,
.server-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
}

.shelf-head {
  justify-content: flex-start;
}

.shelf-icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex: none;
  border-radius: 7px;
  background: var(--surface-soft);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.active .shelf-icon {
  background: #10b981;
  color: white;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.tool-chip,
.empty-chip,
.call-card,
.result-card {
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  overflow-wrap: anywhere;
  font-size: 12px;
  line-height: 1.35;
}

.tool-chip {
  background: var(--surface);
  color: var(--text);
  font-family: var(--font-mono);
}

.tool-chip.external {
  border-color: #10b981;
  background: #ecfdf5;
  color: #047857;
}

.tool-chip.selected,
.call-card.sending {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.empty-chip {
  border-style: dashed;
  color: var(--text-muted);
  text-align: center;
}

.wide {
  grid-column: 1 / -1;
}

.status-pill {
  border-radius: 999px;
  background: var(--surface-soft);
  color: var(--text-muted);
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
}

.status-pill.connected {
  background: #dcfce7;
  color: #15803d;
}

.call-card {
  display: block;
  background: var(--surface-soft);
}

.result-card {
  border-color: #10b981;
  background: #ecfdf5;
  color: #047857;
}

@media (max-width: 900px) {
  .mcp-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .mcp-panel {
    padding: 12px;
  }

  .tool-grid {
    grid-template-columns: 1fr;
  }
}
</style>
