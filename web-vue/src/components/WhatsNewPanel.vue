<template>
  <section v-if="hasChanges" class="whats-new-panel">
    <h2>{{ app.t("version", "whats_new") }}</h2>
    <div class="whats-new-grid">
      <article v-if="diff?.newClasses.length" class="whats-new-card">
        <h3>{{ app.t("diff", "new_classes") }}</h3>
        <div class="whats-new-class-list">
          <span v-for="item in diff.newClasses" :key="item">{{ item }}</span>
        </div>
      </article>
      <article v-if="diff?.newTools.length" class="whats-new-card">
        <h3>{{ app.t("diff", "new_tools") }}</h3>
        <div class="whats-new-tool-list">
          <span v-for="item in diff.newTools" :key="item">{{ item }}</span>
        </div>
      </article>
      <article v-if="diff?.newFunctions.length" class="whats-new-card">
        <h3>{{ app.t("diff", "new_functions") }}</h3>
        <ul>
          <li v-for="item in diff.newFunctions" :key="item"><span>def</span> {{ item }}()</li>
        </ul>
      </article>
      <article class="whats-new-card">
        <h3>{{ app.t("diff", "loc_delta") }}</h3>
        <strong>{{ diff && diff.locDelta >= 0 ? `+${diff.locDelta}` : diff?.locDelta }} lines</strong>
      </article>
    </div>
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
const hasChanges = computed(
  () =>
    !!diff.value &&
    (diff.value.newClasses.length > 0 ||
      diff.value.newTools.length > 0 ||
      diff.value.newFunctions.length > 0 ||
      diff.value.locDelta !== 0),
);
</script>
