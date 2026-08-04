<template>
  <aside class="sidebar">
    <section v-for="layer in app.layers" :key="layer.id" class="sidebar-section">
      <h2>
        <span :class="['layer-dot', `layer-${layer.id}`]" />
        {{ app.t("layer_labels", layer.id) }}
      </h2>
      <RouterLink
        v-for="version in layer.versions"
        :key="version"
        class="sidebar-link"
        :to="`/${app.locale}/${version}`"
      >
        <span>{{ version }}</span>
        {{ app.versionLabel(version) }}
      </RouterLink>
    </section>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
</script>
