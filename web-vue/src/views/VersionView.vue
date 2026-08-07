<template>
  <div class="learn-layout">
    <AppSidebar />
    <section v-if="version" class="content-column version-detail">
      <SessionVisualization :version="version.id" :title="app.t('viz', version.id)" />

      <VersionTabs :tabs="tabs" v-slot="{ active }">
        <MarkdownBlock v-if="active === 'learn'" :content="doc?.content || ''" />
        <SimulatorPanel v-else-if="active === 'simulate' && scenario" :scenario="scenario" />
        <section v-else-if="active === 'simulate'" class="simple-panel">
          <h2>Simulator</h2>
          <p>No scenario data for this version.</p>
        </section>
        <SourcePanel v-else-if="active === 'code'" :filename="version.filename" :source="version.source" />
        <template v-else-if="active === 'deep-dive'">
          <section class="deep-dive-section">
            <h2>{{ app.t("version", "execution_flow") }}</h2>
            <ExecutionFlowPanel :version-id="version.id" />
          </section>
          <section class="deep-dive-section">
            <h2>{{ app.t("compare", "architecture") }}</h2>
            <ArchitecturePanel :version-id="version.id" />
          </section>
          <WhatsNewPanel :version-id="version.id" />
          <DesignDecisionsPanel :version-id="version.id" />
        </template>
      </VersionTabs>
    </section>
    <section v-else class="content-column">
      <h1>Version not found</h1>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import ArchitecturePanel from "@/components/ArchitecturePanel.vue";
import DesignDecisionsPanel from "@/components/DesignDecisionsPanel.vue";
import ExecutionFlowPanel from "@/components/ExecutionFlowPanel.vue";
import MarkdownBlock from "@/components/MarkdownBlock.vue";
import SessionVisualization from "@/components/SessionVisualization.vue";
import SimulatorPanel from "@/components/SimulatorPanel.vue";
import SourcePanel from "@/components/SourcePanel.vue";
import VersionTabs from "@/components/VersionTabs.vue";
import WhatsNewPanel from "@/components/WhatsNewPanel.vue";
import { useAppStore } from "@/stores/app";
import type { Scenario } from "@/types/agent-data";

const route = useRoute();
const app = useAppStore();

const scenarioModules = import.meta.glob("@/data/scenarios/*.json", { eager: true, import: "default" });

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));

const versionId = computed(() => String(route.params.version || ""));
const version = computed(() => app.getVersion(versionId.value));
const doc = computed(() => app.getDoc(versionId.value));
const scenario = computed(() => {
  const key = `/src/data/scenarios/${versionId.value}.json`;
  return scenarioModules[key] as Scenario | undefined;
});

const tabs = computed(() => [
  { id: "learn", label: app.t("version", "tab_learn") },
  { id: "simulate", label: app.t("version", "tab_simulate") },
  { id: "code", label: app.t("version", "tab_code") },
  { id: "deep-dive", label: app.t("version", "tab_deep_dive") },
]);
</script>
