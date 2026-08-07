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

      <div v-if="comparison" class="compare-version-cards">
        <article class="simple-panel">
          <header>
            <h3>{{ app.versionLabel(comparison.left.id) }}</h3>
            <p>{{ app.versionMeta[comparison.left.id]?.subtitle }}</p>
          </header>
          <div class="compare-meta-list">
            <p>{{ comparison.left.loc }} LOC</p>
            <p>{{ comparison.left.tools.length }} tools</p>
            <LayerBadge :layer="app.versionMeta[comparison.left.id].layer">
              {{ app.versionMeta[comparison.left.id].layer }}
            </LayerBadge>
          </div>
        </article>
        <article class="simple-panel">
          <header>
            <h3>{{ app.versionLabel(comparison.right.id) }}</h3>
            <p>{{ app.versionMeta[comparison.right.id]?.subtitle }}</p>
          </header>
          <div class="compare-meta-list">
            <p>{{ comparison.right.loc }} LOC</p>
            <p>{{ comparison.right.tools.length }} tools</p>
            <LayerBadge :layer="app.versionMeta[comparison.right.id].layer">
              {{ app.versionMeta[comparison.right.id].layer }}
            </LayerBadge>
          </div>
        </article>
      </div>

      <section v-if="comparison" class="compare-architecture">
        <h2>{{ app.t("compare", "architecture") }}</h2>
        <div class="code-compare">
          <div>
            <h3>{{ app.versionLabel(comparison.left.id) }}</h3>
            <ArchitecturePanel :version-id="comparison.left.id" />
          </div>
          <div>
            <h3>{{ app.versionLabel(comparison.right.id) }}</h3>
            <ArchitecturePanel :version-id="comparison.right.id" />
          </div>
        </div>
      </section>

      <div v-if="comparison" class="compare-results">
        <article class="stat-card">
          <span>{{ app.t("compare", "loc_delta") }}</span>
          <strong>{{ comparison.locDelta >= 0 ? `+${comparison.locDelta}` : comparison.locDelta }}</strong>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_tools_in_b") }}</span>
          <strong>{{ comparison.toolsOnlyB.length }}</strong>
          <p>{{ comparison.toolsOnlyB.join(", ") || app.t("compare", "none") }}</p>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_classes_in_b") }}</span>
          <strong>{{ comparison.newClasses.length }}</strong>
          <p>{{ comparison.newClasses.join(", ") || app.t("compare", "none") }}</p>
        </article>
        <article class="stat-card">
          <span>{{ app.t("compare", "new_functions_in_b") }}</span>
          <strong>{{ comparison.newFunctions.length }}</strong>
          <p>{{ comparison.newFunctions.join(", ") || app.t("compare", "none") }}</p>
        </article>
      </div>

      <section v-if="comparison" class="simple-panel">
        <h2>{{ app.t("compare", "tool_comparison") }}</h2>
        <div class="tool-columns">
          <article>
            <h3>{{ app.t("compare", "only_in") }} {{ comparison.left.id }}</h3>
            <p>{{ comparison.toolsOnlyA.join(", ") || app.t("compare", "none") }}</p>
          </article>
          <article>
            <h3>{{ app.t("compare", "shared") }}</h3>
            <p>{{ comparison.toolsShared.join(", ") || app.t("compare", "none") }}</p>
          </article>
          <article>
            <h3>{{ app.t("compare", "only_in") }} {{ comparison.right.id }}</h3>
            <p>{{ comparison.toolsOnlyB.join(", ") || app.t("compare", "none") }}</p>
          </article>
        </div>
      </section>

      <CodeDiffPanel
        v-if="comparison"
        :old-source="comparison.left.source"
        :new-source="comparison.right.source"
        :old-label="`${comparison.left.id} (${comparison.left.filename})`"
        :new-label="`${comparison.right.id} (${comparison.right.filename})`"
      />

      <section v-if="!comparison" class="empty-compare">
        <p>{{ app.t("compare", "empty_hint") }}</p>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import ArchitecturePanel from "@/components/ArchitecturePanel.vue";
import CodeDiffPanel from "@/components/CodeDiffPanel.vue";
import LayerBadge from "@/components/LayerBadge.vue";
import { useAppStore } from "@/stores/app";
import { buildVersionComparison } from "@/utils/compare";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));

const data = computed(() => ({ versions: app.allVersions, diffs: app.allDiffs }));
const comparison = computed(() => buildVersionComparison(data.value, app.compareA, app.compareB));
</script>
