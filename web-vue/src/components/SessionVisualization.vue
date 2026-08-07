<template>
  <section v-if="hasVisualization" class="session-visualization-host" data-testid="session-visualization-host">
    <component v-if="VisualizationComponent" :is="VisualizationComponent" :title="title" />
    <div v-else class="session-viz-loading" data-testid="session-visualization-loading" />
  </section>
</template>

<script setup lang="ts">
import { computed, markRaw, onMounted, shallowRef, watch } from "vue";
import type { Component } from "vue";
import { visualizationLoaders } from "./session-visualization-registry";

const props = defineProps<{ version: string; title?: string }>();

const VisualizationComponent = shallowRef<Component | null>(null);
const hasVisualization = computed(() =>
  Boolean(visualizationLoaders[props.version as keyof typeof visualizationLoaders])
);

async function loadVisualization(version: string) {
  const loader = visualizationLoaders[version as keyof typeof visualizationLoaders];
  VisualizationComponent.value = null;
  if (!loader) return;
  const module = await loader();
  VisualizationComponent.value = markRaw(module.default);
}

onMounted(() => loadVisualization(props.version));
watch(() => props.version, loadVisualization);
</script>
