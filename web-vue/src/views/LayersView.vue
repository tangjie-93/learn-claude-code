<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column layers-page">
      <div class="page-heading">
        <h1>{{ app.t("layers", "title") }}</h1>
        <p>{{ app.t("layers", "subtitle") }}</p>
      </div>
      <div class="layer-list">
        <template v-for="(layer, index) in app.layers" :key="layer.id">
          <article :class="['layer-block', `layer-block-${layer.id}`]">
            <header>
              <span :class="['layer-dot', `layer-${layer.id}`]" />
              <div>
                <h2><span>L{{ index + 1 }}</span> {{ app.t("layer_labels", layer.id) }}</h2>
                <p>{{ app.t("layers", layer.id) }}</p>
              </div>
            </header>
            <div class="version-grid compact">
              <RouterLink
                v-for="version in layer.versions"
                :key="version"
                class="layer-version-card"
                :to="`/${app.locale}/${version}`"
              >
                <div class="layer-card-main">
                  <div class="layer-card-copy">
                    <div class="layer-card-badges">
                      <span>{{ version }}</span>
                      <LayerBadge :layer="layer.id">{{ layer.id }}</LayerBadge>
                    </div>
                    <h3>{{ app.versionLabel(version) }}</h3>
                    <p>{{ app.versionMeta[version].subtitle }}</p>
                  </div>
                  <svg class="layer-card-chevron" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="m9 18 6-6-6-6" />
                  </svg>
                </div>
                <div class="layer-card-meta">
                  <span>{{ app.getVersion(version)?.loc ?? "?" }} LOC</span>
                  <span>{{ app.getVersion(version)?.tools.length ?? "?" }} tools</span>
                </div>
                <p v-if="app.versionMeta[version].keyInsight" class="layer-key-insight">
                  {{ app.versionMeta[version].keyInsight }}
                </p>
              </RouterLink>
            </div>
            <div v-if="index < app.layers.length - 1" class="layer-composition-indicator" aria-hidden="true">
              <svg viewBox="0 0 20 12">
                <path d="M10 0v12M5 7l5 5 5-5" />
              </svg>
            </div>
          </article>
        </template>
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
