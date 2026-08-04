<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column">
      <div class="page-heading">
        <h1>{{ app.t("compare", "title") }}</h1>
        <p>{{ app.t("compare", "subtitle") }}</p>
      </div>

      <div class="compare-selectors">
        <label>
          {{ app.t("compare", "select_a") }}
          <select v-model="app.compareA">
            <option value="">-- select --</option>
            <option v-for="version in app.versionOrder" :key="version" :value="version">
              {{ version }} - {{ app.versionLabel(version) }}
            </option>
          </select>
        </label>
        <label>
          {{ app.t("compare", "select_b") }}
          <select v-model="app.compareB">
            <option value="">-- select --</option>
            <option v-for="version in app.versionOrder" :key="version" :value="version">
              {{ version }} - {{ app.versionLabel(version) }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="left && right" class="compare-results">
        <article class="stat-card">
          <span>{{ app.t("compare", "loc_delta") }}</span>
          <strong>{{ locDelta >= 0 ? `+${locDelta}` : locDelta }}</strong>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_tools_in_b") }}</span>
          <strong>{{ toolsOnlyRight.length }}</strong>
          <p>{{ toolsOnlyRight.join(", ") || app.t("compare", "none") }}</p>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_classes_in_b") }}</span>
          <strong>{{ newClasses.length }}</strong>
          <p>{{ newClasses.join(", ") || app.t("compare", "none") }}</p>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_functions_in_b") }}</span>
          <strong>{{ newFunctions.length }}</strong>
          <p>{{ newFunctions.join(", ") || app.t("compare", "none") }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));

const left = computed(() => app.getVersion(app.compareA));
const right = computed(() => app.getVersion(app.compareB));
const locDelta = computed(() => (right.value?.loc ?? 0) - (left.value?.loc ?? 0));
const toolsOnlyRight = computed(() => {
  const leftTools = new Set(left.value?.tools ?? []);
  return (right.value?.tools ?? []).filter((tool) => !leftTools.has(tool));
});
const newClasses = computed(() => {
  const leftClasses = new Set((left.value?.classes ?? []).map((item) => item.name));
  return (right.value?.classes ?? []).map((item) => item.name).filter((name) => !leftClasses.has(name));
});
const newFunctions = computed(() => {
  const leftFunctions = new Set((left.value?.functions ?? []).map((item) => item.name));
  return (right.value?.functions ?? []).map((item) => item.name).filter((name) => !leftFunctions.has(name));
});
</script>
