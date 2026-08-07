<template>
  <section class="simple-panel whats-new-panel">
    <h2>What changed</h2>
    <div v-if="diff" class="diff-grid">
      <article>
        <strong>{{ diff.locDelta >= 0 ? `+${diff.locDelta}` : diff.locDelta }}</strong>
        <span>LOC</span>
      </article>
      <article>
        <strong>{{ diff.newTools.length }}</strong>
        <span>new tools</span>
      </article>
      <article>
        <strong>{{ diff.newClasses.length }}</strong>
        <span>new classes</span>
      </article>
      <article>
        <strong>{{ diff.newFunctions.length }}</strong>
        <span>new functions</span>
      </article>
    </div>
    <p v-else>This is the baseline version.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAppStore } from "@/stores/app";
import { getVersionDiffSummary } from "@/utils/learning";

const props = defineProps<{ versionId: string }>();
const app = useAppStore();
const data = computed(() => ({ versions: app.allVersions, diffs: app.allDiffs }));
const diff = computed(() => getVersionDiffSummary(data.value, props.versionId));
</script>
