<template>
  <section class="decisions-panel">
    <h2>{{ app.t("version", "design_decisions") }}</h2>
    <div v-if="decisions.length" class="decision-list">
      <article v-for="decision in decisions" :key="decision.id" class="decision-card">
        <button class="decision-trigger" type="button" @click="toggleDecision(decision.id)">
          <span>{{ decision.title }}</span>
          <svg :class="{ open: openDecisionIds.has(decision.id) }" viewBox="0 0 24 24" aria-hidden="true">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>
        <div v-if="openDecisionIds.has(decision.id)" class="decision-body">
          <p>{{ decision.description }}</p>
          <small v-if="decision.alternatives">{{ decision.alternatives }}</small>
        </div>
      </article>
    </div>
    <p v-else>Design decisions are not available for this lesson yet.</p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useAppStore } from "@/stores/app";
import { getDesignDecisions } from "@/utils/deep-dive";

const props = defineProps<{ versionId: string }>();
const app = useAppStore();
const decisions = computed(() => getDesignDecisions(props.versionId, app.locale));
const openDecisionIds = ref(new Set<string>());

function toggleDecision(id: string) {
  const next = new Set(openDecisionIds.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  openDecisionIds.value = next;
}
</script>
