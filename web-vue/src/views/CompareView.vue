<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column compare-page">
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
        <span class="compare-arrow" aria-hidden="true">→</span>
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
        <article class="stat-card stat-card-loc">
          <header>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6M8 13h8M8 17h5" />
            </svg>
            <span>{{ app.t("compare", "loc_delta") }}</span>
          </header>
          <strong>
            <span>{{ comparison.locDelta >= 0 ? `+${comparison.locDelta}` : comparison.locDelta }}</span>
            <small>{{ app.t("compare", "lines") }}</small>
          </strong>
        </article>
        <article class="stat-card stat-card-tools">
          <header>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="m14.7 6.3 3 3M5 19l6.5-6.5M13 5l6 6-8 8H5v-6z" />
            </svg>
            <span>{{ app.t("compare", "new_tools_in_b") }}</span>
          </header>
          <strong>{{ comparison.toolsOnlyB.length }}</strong>
          <div v-if="comparison.toolsOnlyB.length" class="stat-tag-list">
            <span v-for="tool in comparison.toolsOnlyB" :key="tool">{{ tool }}</span>
          </div>
        </article>
        <article class="stat-card stat-card-classes">
          <header>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              <path d="M3.3 7 12 12l8.7-5M12 22V12" />
            </svg>
            <span>{{ app.t("compare", "new_classes_in_b") }}</span>
          </header>
          <strong>{{ comparison.newClasses.length }}</strong>
          <div v-if="comparison.newClasses.length" class="stat-tag-list">
            <span v-for="item in comparison.newClasses" :key="item">{{ item }}</span>
          </div>
        </article>
        <article class="stat-card stat-card-functions">
          <header>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M8 21s4-9 4-18M7 5h10M5 12h14" />
            </svg>
            <span>{{ app.t("compare", "new_functions_in_b") }}</span>
          </header>
          <strong>{{ comparison.newFunctions.length }}</strong>
          <div v-if="comparison.newFunctions.length" class="stat-tag-list">
            <span v-for="item in comparison.newFunctions" :key="item">{{ item }}</span>
          </div>
        </article>
      </div>

      <section v-if="comparison" class="simple-panel tool-comparison-panel">
        <h2>{{ app.t("compare", "tool_comparison") }}</h2>
        <div class="tool-columns">
          <article>
            <h3>{{ app.t("compare", "only_in") }} {{ app.versionLabel(comparison.left.id) }}</h3>
            <p v-if="!comparison.toolsOnlyA.length">{{ app.t("compare", "none") }}</p>
            <div v-else class="tool-pill-list only-left">
              <span v-for="tool in comparison.toolsOnlyA" :key="tool">{{ tool }}</span>
            </div>
          </article>
          <article>
            <h3>{{ app.t("compare", "shared") }}</h3>
            <p v-if="!comparison.toolsShared.length">{{ app.t("compare", "none") }}</p>
            <div v-else class="tool-pill-list shared">
              <span v-for="tool in comparison.toolsShared" :key="tool">{{ tool }}</span>
            </div>
          </article>
          <article>
            <h3>{{ app.t("compare", "only_in") }} {{ app.versionLabel(comparison.right.id) }}</h3>
            <p v-if="!comparison.toolsOnlyB.length">{{ app.t("compare", "none") }}</p>
            <div v-else class="tool-pill-list only-right">
              <span v-for="tool in comparison.toolsOnlyB" :key="tool">{{ tool }}</span>
            </div>
          </article>
        </div>
      </section>

      <section v-if="comparison" class="source-diff-section">
        <h2>{{ app.t("compare", "source_diff") }}</h2>
        <CodeDiffPanel
          :old-source="comparison.left.source"
          :new-source="comparison.right.source"
          :old-label="`${comparison.left.id} (${comparison.left.filename})`"
          :new-label="`${comparison.right.id} (${comparison.right.filename})`"
        />
      </section>

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
