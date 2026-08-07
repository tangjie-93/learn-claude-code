<template>
  <section class="skill-loading-vis" data-testid="s07-skill-loading">
    <h2>{{ title || "On-Demand Skill Loading" }}</h2>

    <div class="stage">
      <div class="content-row">
        <div class="main-column">
          <article class="system-block">
            <div class="section-label">
              <span class="status-dot neutral" />
              <span>System Prompt</span>
              <span class="tag neutral-tag">always present</span>
            </div>

            <div class="catalog">
              <div class="catalog-title"># Available Skills</div>
              <div class="skill-list">
                <div
                  v-for="skill in SKILLS"
                  :key="skill.name"
                  :class="['skill-summary', { highlighted: skill.name === highlightedSkillName }]"
                >
                  <strong>{{ skill.name }}</strong>
                  <span> - {{ skill.summary }}</span>
                </div>
              </div>
            </div>
          </article>

          <Transition name="fade-slide" mode="out-in">
            <div v-if="invokedSkill" :key="invokedSkill.name" class="invocation">
              <span>User types:</span>
              <code>{{ invokedSkill.name }}</code>
            </div>
          </Transition>

          <Transition name="grow-fade">
            <div v-if="showInjectedContent" class="connector" aria-label="Skill content injected into context">
              <span class="connector-line" />
              <span class="connector-arrow" />
            </div>
          </Transition>

          <div class="injected-stack">
            <Transition name="grow-fade">
              <SkillContentBlock
                v-if="showFirstContent"
                :skill="SKILLS[0]"
                tone="blue"
                :faded="firstContentFaded"
              />
            </Transition>

            <Transition name="grow-fade">
              <SkillContentBlock v-if="showSecondContent" :skill="SKILLS[1]" tone="violet" />
            </Transition>
          </div>

          <Transition name="fade">
            <div v-if="currentStep === 3" class="mechanism-note">
              The Skill tool returns content as a tool_result message. The model sees it in context and follows the
              instructions. No system prompt bloat.
            </div>
          </Transition>

          <Transition name="fade">
            <div v-if="currentStep === 5" class="layer-summary">
              <div class="layer-card">
                <strong>LAYER 1</strong>
                <span>Always present, ~120 tokens</span>
              </div>
              <div class="layer-card demand">
                <strong>LAYER 2</strong>
                <span>On demand, ~300-500 tokens each</span>
              </div>
            </div>
          </Transition>
        </div>

        <aside class="token-gauge" aria-label="Token count">
          <div class="token-label">Tokens</div>
          <div class="gauge-track">
            <div :class="['gauge-fill', tokenTone]" :style="{ height: `${tokenPct}%` }" />
          </div>
          <div class="token-count">{{ tokenCount }}</div>
        </aside>
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
import { computed, defineComponent, h } from "vue";
import { useSteppedVisualization } from "../../composables/stepped-visualization";
import StepControls from "./StepControls.vue";

interface SkillEntry {
  name: string;
  summary: string;
  fullTokens: number;
  content: string[];
}

type SkillTone = "blue" | "violet";

defineProps<{
  title?: string;
}>();

const SKILLS: SkillEntry[] = [
  {
    name: "/commit",
    summary: "Create git commits following repo conventions",
    fullTokens: 320,
    content: [
      "1. Run git status + git diff to see changes",
      "2. Analyze all staged changes and draft message",
      "3. Create commit with Co-Authored-By trailer",
      "4. Run git status after commit to verify",
    ],
  },
  {
    name: "/review-pr",
    summary: "Review pull requests for bugs and style",
    fullTokens: 480,
    content: [
      "1. Fetch PR diff via gh pr view",
      "2. Analyze changes file by file for issues",
      "3. Check for bugs, security, and style problems",
      "4. Post review comments with gh pr review",
    ],
  },
  {
    name: "/test",
    summary: "Run and analyze test suites",
    fullTokens: 290,
    content: [
      "1. Detect test framework from package.json",
      "2. Run test suite and capture output",
      "3. Analyze failures and suggest fixes",
      "4. Re-run after applying fixes",
    ],
  },
  {
    name: "/deploy",
    summary: "Deploy application to target environment",
    fullTokens: 350,
    content: [
      "1. Verify all tests pass before deploy",
      "2. Build production bundle",
      "3. Push to deployment target via CI",
      "4. Verify health check on deployed URL",
    ],
  },
];

const TOKEN_STATES = [120, 120, 440, 440, 780, 780] as const;
const MAX_TOKEN_DISPLAY = 1000;

const STEPS = [
  {
    title: "Layer 1: Compact Summaries",
    description: "All skills are summarized in the system prompt. Compact, always present.",
  },
  {
    title: "Skill Invocation",
    description: "The model recognizes a skill invocation and triggers the Skill tool.",
  },
  {
    title: "Layer 2: Full Injection",
    description: "The full skill instructions are injected as a tool_result, not into the system prompt.",
  },
  {
    title: "In Context Now",
    description: "The detailed instructions appear as if a tool returned them. The model follows them precisely.",
  },
  {
    title: "Stack Skills",
    description: "Multiple skills can be loaded. Only summaries are permanent; full content comes and goes.",
  },
  {
    title: "Two-Layer Architecture",
    description: "Layer 1: always present, tiny. Layer 2: loaded on demand, detailed. Elegant separation.",
  },
] as const;

const { currentStep, totalSteps, next, prev, reset, isPlaying, toggleAutoPlay } = useSteppedVisualization({
  totalSteps: STEPS.length,
  autoPlayInterval: 2500,
});

const current = computed(() => STEPS[currentStep.value]);
const tokenCount = computed(() => TOKEN_STATES[currentStep.value]);
const tokenPct = computed(() => (tokenCount.value / MAX_TOKEN_DISPLAY) * 100);
const tokenTone = computed(() => {
  if (tokenCount.value > 600) return "high";
  if (tokenCount.value > 300) return "medium";
  return "low";
});
const highlightedSkillName = computed(() => {
  if (currentStep.value >= 1 && currentStep.value <= 3) return SKILLS[0].name;
  if (currentStep.value >= 4) return SKILLS[1].name;
  return "";
});
const invokedSkill = computed(() => {
  if (currentStep.value === 1) return SKILLS[0];
  if (currentStep.value === 4) return SKILLS[1];
  return null;
});
const showFirstContent = computed(() => currentStep.value >= 2);
const showSecondContent = computed(() => currentStep.value >= 4);
const showInjectedContent = computed(() => showFirstContent.value || showSecondContent.value);
const firstContentFaded = computed(() => currentStep.value >= 5);

const SkillContentBlock = defineComponent({
  props: {
    skill: { type: Object as () => SkillEntry, required: true },
    tone: { type: String as () => SkillTone, required: true },
    faded: { type: Boolean, default: false },
  },
  setup(props) {
    return () =>
      h("article", { class: ["content-block", `tone-${props.tone}`, { faded: props.faded }] }, [
        h("div", { class: "content-head" }, [
          h("div", { class: "content-title" }, [
            h("span", { class: "status-dot" }),
            h("span", `SKILL.md: ${props.skill.name}`),
          ]),
          h("span", { class: "tag result-tag" }, "tool_result"),
        ]),
        h(
          "div",
          { class: "content-lines" },
          props.skill.content.map((line, index) =>
            h("div", { key: line, class: "content-line", style: { transitionDelay: `${index * 60}ms` } }, line),
          ),
        ),
      ]);
  },
});
</script>

<style scoped>
.skill-loading-vis {
  min-height: 500px;
  color: #18181b;
}

.skill-loading-vis h2 {
  margin: 0 0 16px;
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

.content-row {
  display: flex;
  gap: 24px;
  min-height: 390px;
}

.main-column {
  min-width: 0;
  flex: 1;
}

.system-block,
.injected-stack {
  margin-bottom: 12px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #52525b;
  font-size: 12px;
  font-weight: 650;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: currentColor;
}

.status-dot.neutral {
  background: #a1a1aa;
}

.tag {
  border-radius: 4px;
  padding: 2px 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
  line-height: 1.2;
}

.neutral-tag {
  background: #f4f4f5;
  color: #71717a;
}

.catalog {
  border: 1px solid #3f3f46;
  border-radius: 8px;
  background: #18181b;
  padding: 16px;
}

.catalog-title {
  margin-bottom: 8px;
  color: #71717a;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 10px;
}

.skill-list {
  display: grid;
  gap: 6px;
}

.skill-summary {
  border-radius: 6px;
  background: #27272a;
  color: #a1a1aa;
  padding: 7px 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.35;
  transition:
    background-color 240ms ease,
    box-shadow 240ms ease,
    color 240ms ease;
}

.skill-summary strong {
  color: #e4e4e7;
  font-weight: 700;
}

.skill-summary.highlighted {
  background: rgba(30, 64, 175, 0.78);
  box-shadow: 0 0 12px 2px rgba(37, 99, 235, 0.4);
  color: #bfdbfe;
}

.invocation {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #eff6ff;
  padding: 8px 12px;
  color: #2563eb;
  font-size: 12px;
}

.invocation code {
  border-radius: 4px;
  background: #dbeafe;
  padding: 2px 8px;
  color: #1e40af;
  font-size: 12px;
  font-weight: 700;
}

.connector {
  display: flex;
  align-items: center;
  flex-direction: column;
  margin: 6px 0;
}

.connector-line {
  width: 1px;
  height: 24px;
  background: #3b82f6;
}

.connector-arrow {
  width: 0;
  height: 0;
  border-right: 5px solid transparent;
  border-left: 5px solid transparent;
  border-top: 6px solid #3b82f6;
}

.injected-stack {
  display: grid;
  gap: 12px;
}

.content-block {
  overflow: hidden;
  border: 2px solid;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
  transition: opacity 220ms ease;
}

.content-block.faded {
  opacity: 0.42;
}

.content-block.tone-blue {
  border-color: #93c5fd;
}

.content-block.tone-violet {
  border-color: #c4b5fd;
}

.content-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.content-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 800;
}

.tone-blue .content-title {
  color: #1d4ed8;
}

.tone-violet .content-title {
  color: #6d28d9;
}

.result-tag {
  background: #eff6ff;
  color: #2563eb;
}

.tone-violet .result-tag {
  background: #f5f3ff;
  color: #7c3aed;
}

.content-lines {
  display: grid;
  gap: 4px;
}

.content-line {
  color: #52525b;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.45;
}

.mechanism-note {
  margin-top: 12px;
  border: 1px solid #fcd34d;
  border-radius: 6px;
  background: #fffbeb;
  padding: 8px 12px;
  color: #92400e;
  font-size: 12px;
  line-height: 1.45;
}

.layer-summary {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.layer-card {
  flex: 1;
  border: 1px solid #e4e4e7;
  border-radius: 6px;
  background: #fafafa;
  padding: 8px;
  text-align: center;
}

.layer-card strong,
.layer-card span {
  display: block;
}

.layer-card strong {
  color: #71717a;
  font-size: 10px;
}

.layer-card span {
  color: #52525b;
  font-size: 12px;
}

.layer-card.demand {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.layer-card.demand strong,
.layer-card.demand span {
  color: #2563eb;
}

.token-gauge {
  display: flex;
  width: 64px;
  flex: 0 0 64px;
  align-items: center;
  flex-direction: column;
}

.token-label,
.token-count {
  text-align: center;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.token-label {
  margin-bottom: 4px;
  color: #71717a;
  font-size: 10px;
}

.gauge-track {
  position: relative;
  width: 32px;
  height: 300px;
  overflow: hidden;
  border-radius: 999px;
  background: #f4f4f5;
}

.gauge-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  border-radius: 999px;
  transition:
    height 300ms ease,
    background-color 220ms ease;
}

.gauge-fill.low {
  background: #10b981;
}

.gauge-fill.medium {
  background: #3b82f6;
}

.gauge-fill.high {
  background: #f59e0b;
}

.token-count {
  margin-top: 8px;
  color: #52525b;
  font-size: 12px;
  font-weight: 800;
}

.fade-enter-active,
.fade-leave-active,
.fade-slide-enter-active,
.fade-slide-leave-active,
.grow-fade-enter-active,
.grow-fade-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.fade-enter-from,
.fade-leave-to,
.fade-slide-enter-from,
.fade-slide-leave-to,
.grow-fade-enter-from,
.grow-fade-leave-to {
  opacity: 0;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  transform: translateY(-8px);
}

.grow-fade-enter-from,
.grow-fade-leave-to {
  transform: scaleY(0.98);
}

@media (max-width: 720px) {
  .stage {
    padding: 14px;
  }

  .content-row {
    flex-direction: column;
    gap: 16px;
  }

  .token-gauge {
    width: 100%;
    flex: none;
    align-items: stretch;
  }

  .gauge-track {
    width: 100%;
    height: 18px;
  }

  .gauge-fill {
    height: 100% !important;
  }

  .layer-summary {
    flex-direction: column;
  }
}
</style>
