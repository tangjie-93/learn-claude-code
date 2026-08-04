<template>
  <div class="app-shell">
    <AppHeader />
    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { RouterView } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();

onMounted(() => {
  app.hydrateTheme();
});

watch(
  () => app.isDark,
  (isDark) => {
    document.documentElement.classList.toggle("dark", isDark);
  },
  { immediate: true },
);
</script>
