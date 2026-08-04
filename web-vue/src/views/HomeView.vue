<template>
  <div class="home-view">
    <section class="hero">
      <p class="eyebrow">Vue 3 + TypeScript</p>
      <h1>{{ app.t("home", "hero_title") }}</h1>
      <p>{{ app.t("home", "hero_subtitle") }}</p>
      <RouterLink class="primary-action" :to="`/${app.locale}/timeline`">
        {{ app.t("home", "start") }}
      </RouterLink>
    </section>

    <section class="section">
      <div class="section-heading">
        <h2>{{ app.t("home", "learning_path") }}</h2>
        <p>{{ app.t("home", "learning_path_desc") }}</p>
      </div>
      <div class="version-grid">
        <RouterLink
          v-for="id in app.versionOrder"
          :key="id"
          class="version-card"
          :to="`/${app.locale}/${id}`"
        >
          <div class="card-topline">
            <LayerBadge :layer="app.versionMeta[id].layer">{{ id }}</LayerBadge>
            <span>{{ app.getVersion(id)?.loc ?? 0 }} LOC</span>
          </div>
          <h3>{{ app.versionLabel(id) }}</h3>
          <p>{{ app.versionMeta[id].keyInsight }}</p>
        </RouterLink>
      </div>
    </section>

    <section class="section">
      <div class="section-heading">
        <h2>{{ app.t("home", "layers_title") }}</h2>
        <p>{{ app.t("home", "layers_desc") }}</p>
      </div>
      <div class="layer-list">
        <article v-for="layer in app.layers" :key="layer.id" class="layer-row">
          <div :class="['layer-stripe', `layer-${layer.id}`]" />
          <div>
            <h3>{{ app.t("layer_labels", layer.id) }}</h3>
            <div class="badge-row">
              <RouterLink v-for="version in layer.versions" :key="version" :to="`/${app.locale}/${version}`">
                <LayerBadge :layer="layer.id">{{ version }}</LayerBadge>
              </RouterLink>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterLink, useRoute } from "vue-router";
import LayerBadge from "@/components/LayerBadge.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));
</script>
