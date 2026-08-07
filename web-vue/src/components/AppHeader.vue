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
        <svg v-if="mobileOpen" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M6 6l12 12M18 6L6 18" />
        </svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M4 7h16M4 12h16M4 17h16" />
        </svg>
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
          <svg v-if="app.isDark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
            <circle cx="12" cy="12" r="4" />
          </svg>
          <svg v-else viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M20 12.2A8 8 0 1 1 11.8 4 6.5 6.5 0 0 0 20 12.2Z" />
          </svg>
        </button>
        <a
          class="github-link"
          href="https://github.com/shareAI-lab/learn-claude-code"
          target="_blank"
          rel="noopener"
          aria-label="GitHub"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.2-3.5-1.2-.4-1-.9-1.3-.9-1.3-.7-.5.1-.5.1-.5.8.1 1.3.8 1.3.8.7 1.3 1.9.9 2.4.7.1-.5.3-.9.6-1.2-2.3-.3-4.7-1.1-4.7-5.1 0-1.1.4-2 1.1-2.7-.1-.3-.5-1.3.1-2.7 0 0 .9-.3 2.8 1a9.8 9.8 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .6 1.4.2 2.4.1 2.7.7.7 1.1 1.6 1.1 2.7 0 4-2.4 4.8-4.7 5.1.3.3.6.8.6 1.6v2.3c0 .3.2.6.7.5A10 10 0 0 0 12 2Z" />
          </svg>
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
        <button class="icon-button" type="button" aria-label="Toggle theme" @click="app.toggleTheme">
          <svg v-if="app.isDark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
            <circle cx="12" cy="12" r="4" />
          </svg>
          <svg v-else viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M20 12.2A8 8 0 1 1 11.8 4 6.5 6.5 0 0 0 20 12.2Z" />
          </svg>
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
