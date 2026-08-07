<template>
  <section class="simple-panel decisions-panel">
    <h2>Design decisions</h2>
    <div v-if="decisions.length" class="decision-list">
      <details v-for="decision in decisions" :key="decision.id">
        <summary>{{ decision.title }}</summary>
        <p>{{ decision.description }}</p>
        <small v-if="decision.alternatives">{{ decision.alternatives }}</small>
      </details>
    </div>
    <p v-else>Design decisions are not available for this lesson yet.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAppStore } from "@/stores/app";
import { getDesignDecisions } from "@/utils/deep-dive";

const props = defineProps<{ versionId: string }>();
const app = useAppStore();
const decisions = computed(() => getDesignDecisions(props.versionId, app.locale));
</script>
