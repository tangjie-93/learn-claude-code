<template>
  <header class="app-header">
    <RouterLink class="brand" :to="`/${app.locale}`">Learn Claude Code</RouterLink>
    <nav class="nav-links">
      <RouterLink :to="`/${app.locale}/timeline`">{{ app.t("nav", "timeline") }}</RouterLink>
      <RouterLink :to="`/${app.locale}/compare`">{{ app.t("nav", "compare") }}</RouterLink>
      <RouterLink :to="`/${app.locale}/layers`">{{ app.t("nav", "layers") }}</RouterLink>
    </nav>
    <div class="header-actions">
      <select :value="app.locale" aria-label="Language" @change="switchLocale">
        <option value="en">EN</option>
        <option value="zh">中文</option>
        <option value="ja">日本語</option>
      </select>
      <button class="icon-button" type="button" @click="app.toggleTheme">
        {{ app.isDark ? "Light" : "Dark" }}
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();
const router = useRouter();

function switchLocale(event: Event) {
  const next = (event.target as HTMLSelectElement).value;
  const current = String(route.params.locale || app.locale);
  app.setLocale(next);
  router.push(route.fullPath.replace(`/${current}`, `/${next}`));
}
</script>
