<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column">
      <div class="page-heading">
        <h1>{{ app.t("layers", "title") }}</h1>
        <p>{{ app.t("layers", "subtitle") }}</p>
      </div>
      <div class="layer-list">
        <article v-for="(layer, index) in app.layers" :key="layer.id" class="layer-block">
          <header>
            <span :class="['layer-dot', `layer-${layer.id}`]" />
            <div>
              <h2>L{{ index + 1 }} · {{ app.t("layer_labels", layer.id) }}</h2>
              <p>{{ app.t("layers", layer.id) }}</p>
            </div>
          </header>
          <div class="version-grid compact">
            <RouterLink
              v-for="version in layer.versions"
              :key="version"
              class="version-card"
              :to="`/${app.locale}/${version}`"
            >
              <LayerBadge :layer="layer.id">{{ version }}</LayerBadge>
              <h3>{{ app.versionLabel(version) }}</h3>
              <p>{{ app.versionMeta[version].subtitle }}</p>
            </RouterLink>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterLink, useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import LayerBadge from "@/components/LayerBadge.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));
</script>
