<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column">
      <div class="page-heading">
        <h1>{{ app.t("timeline", "title") }}</h1>
        <p>{{ app.t("timeline", "subtitle") }}</p>
      </div>
      <section class="timeline-legend">
        <h3>{{ app.t("timeline", "layer_legend") }}</h3>
        <div class="legend-row">
          <span v-for="layer in layerLegend" :key="layer.id">
            <i :class="['layer-dot', `layer-${layer.id}`]" />
            {{ layer.label }}
          </span>
        </div>
      </section>

      <div class="timeline-list">
        <div v-for="(id, index) in app.versionOrder" :key="id" class="timeline-node">
          <div class="timeline-rail">
            <span :class="['timeline-dot', `layer-${app.versionMeta[id].layer}`]">
              {{ id.replace("s", "").replace("_mini", "m") }}
            </span>
            <i
              v-if="index < app.versionOrder.length - 1"
              :class="['timeline-line', `layer-${app.versionMeta[app.versionOrder[index + 1]].layer}`]"
            />
          </div>
          <div class="timeline-card-wrap">
            <RouterLink class="timeline-card" :to="`/${app.locale}/${id}`">
              <div class="badge-row">
                <LayerBadge :layer="app.versionMeta[id].layer">{{ id }}</LayerBadge>
                <span>{{ app.versionMeta[id].coreAddition }}</span>
              </div>
              <h3>
                {{ app.versionLabel(id) }}
                <span>{{ app.versionMeta[id].subtitle }}</span>
              </h3>
              <div class="timeline-stats">
                <span>{{ app.getVersion(id)?.loc ?? 0 }} {{ app.t("version", "loc") }}</span>
                <span>{{ app.getVersion(id)?.tools.length ?? 0 }} {{ app.t("version", "tools") }}</span>
              </div>
              <div class="loc-meter">
                <span :class="`layer-${app.versionMeta[id].layer}`" :style="{ width: `${locRows[index]?.percent ?? 2}%` }" />
              </div>
              <p v-if="app.versionMeta[id].keyInsight">
                &quot;{{ app.versionMeta[id].keyInsight }}&quot;
              </p>
              <strong>{{ app.t("timeline", "learn_more") }} →</strong>
            </RouterLink>
          </div>
        </div>
      </div>

      <section class="simple-panel">
        <h3>{{ app.t("timeline", "loc_growth") }}</h3>
        <div class="loc-growth">
          <div v-for="row in locRows" :key="row.id">
            <span>{{ row.id }}</span>
            <div><i :class="`layer-${row.layer}`" :style="{ width: `${row.percent}%` }" /></div>
            <strong>{{ row.loc }}</strong>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { onBeforeMount } from "vue";
import { RouterLink, useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import LayerBadge from "@/components/LayerBadge.vue";
import { useAppStore } from "@/stores/app";
import { getLayerLegend, getLocGrowthRows } from "@/utils/learning";

const app = useAppStore();
const route = useRoute();
const layerLegend = getLayerLegend();
const locRows = computed(() => getLocGrowthRows(app.allVersions));

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));
</script>
