<template>
  <div class="learn-layout">
    <AppSidebar />
    <section class="content-column">
      <div class="page-heading">
        <h1>{{ app.t("timeline", "title") }}</h1>
        <p>{{ app.t("timeline", "subtitle") }}</p>
      </div>
      <div class="timeline">
        <RouterLink
          v-for="(id, index) in app.versionOrder"
          :key="id"
          class="timeline-item"
          :to="`/${app.locale}/${id}`"
        >
          <span class="timeline-index">{{ index + 1 }}</span>
          <div>
            <h2>{{ id }} · {{ app.versionLabel(id) }}</h2>
            <p>{{ app.versionMeta[id].keyInsight }}</p>
          </div>
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterLink, useRoute } from "vue-router";
import AppSidebar from "@/components/AppSidebar.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));
</script>
