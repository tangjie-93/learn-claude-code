<template>
  <header class="app-header">
    <div class="app-header-inner">
      <RouterLink class="brand" :to="`/${app.locale}`">Learn Claude Code</RouterLink>
      <button
        class="mobile-menu-button"
        data-testid="mobile-menu-button"
        type="button"
        :aria-expanded="mobileOpen"
        aria-label="Toggle navigation"
        @click="mobileOpen = !mobileOpen"
      >
        {{ mobileOpen ? "x" : "menu" }}
      </button>
      <nav class="nav-links">
        <RouterLink :to="`/${app.locale}/timeline`">{{ app.t("nav", "timeline") }}</RouterLink>
        <RouterLink :to="`/${app.locale}/compare`">{{ app.t("nav", "compare") }}</RouterLink>
        <RouterLink :to="`/${app.locale}/layers`">{{ app.t("nav", "layers") }}</RouterLink>
      </nav>
      <div class="header-actions">
        <div class="locale-tabs" aria-label="Language">
          <button
            v-for="locale in locales"
            :key="locale.code"
            :class="{ active: app.locale === locale.code }"
            type="button"
            @click="switchLocale(locale.code)"
          >
            {{ locale.label }}
          </button>
        </div>
        <button class="icon-button" type="button" aria-label="Toggle theme" @click="app.toggleTheme">
          {{ app.isDark ? "sun" : "moon" }}
        </button>
        <a
          class="github-link"
          href="https://github.com/shareAI-lab/learn-claude-code"
          target="_blank"
          rel="noopener"
          aria-label="GitHub"
        >
          GitHub
        </a>
      </div>
    </div>
    <nav v-if="mobileOpen" class="mobile-menu" data-testid="mobile-menu">
      <RouterLink :to="`/${app.locale}/timeline`" @click="mobileOpen = false">{{ app.t("nav", "timeline") }}</RouterLink>
      <RouterLink :to="`/${app.locale}/compare`" @click="mobileOpen = false">{{ app.t("nav", "compare") }}</RouterLink>
      <RouterLink :to="`/${app.locale}/layers`" @click="mobileOpen = false">{{ app.t("nav", "layers") }}</RouterLink>
      <div class="mobile-menu-actions">
        <div class="locale-tabs" aria-label="Language">
          <button
            v-for="locale in locales"
            :key="locale.code"
            :class="{ active: app.locale === locale.code }"
            type="button"
            @click="switchLocale(locale.code)"
          >
            {{ locale.label }}
          </button>
        </div>
        <button class="icon-button" type="button" @click="app.toggleTheme">
          {{ app.isDark ? "sun" : "moon" }}
        </button>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();
const router = useRouter();
const mobileOpen = ref(false);
const locales = [
  { code: "en", label: "EN" },
  { code: "zh", label: "中文" },
  { code: "ja", label: "日本語" },
] as const;

function switchLocale(next: string) {
  const current = String(route.params.locale || app.locale);
  app.setLocale(next);
  mobileOpen.value = false;
  router.push(route.fullPath.replace(`/${current}`, `/${next}`));
}
</script>
