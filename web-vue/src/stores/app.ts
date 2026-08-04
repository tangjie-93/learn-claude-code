import { defineStore } from "pinia";
import { computed, ref } from "vue";
import docs from "@/data/generated/docs.json";
import versions from "@/data/generated/versions.json";
import en from "@/i18n/messages/en.json";
import zh from "@/i18n/messages/zh.json";
import ja from "@/i18n/messages/ja.json";
import { layers, locales, versionMeta, versionOrder, type Locale } from "@/data/constants";
import type { DocContent, VersionIndex } from "@/types/agent-data";

const messages = { en, zh, ja } as const;
const versionIndex = versions as VersionIndex;
const docItems = docs as DocContent[];

export const useAppStore = defineStore("app", () => {
  const locale = ref<Locale>("en");
  const isDark = ref(false);
  const compareA = ref("");
  const compareB = ref("");

  const allVersions = computed(() => versionIndex.versions);
  const allDiffs = computed(() => versionIndex.diffs);

  function setLocale(next: string) {
    locale.value = locales.includes(next as Locale) ? (next as Locale) : "en";
  }

  function t(namespace: string, key: string) {
    const bundle = messages[locale.value] as Record<string, Record<string, string>>;
    const fallback = messages.en as Record<string, Record<string, string>>;
    return bundle[namespace]?.[key] ?? fallback[namespace]?.[key] ?? key;
  }

  function versionLabel(id: string) {
    return t("sessions", id) || versionMeta[id]?.title || id;
  }

  function getVersion(id: string) {
    return versionIndex.versions.find((version) => version.id === id);
  }

  function getDoc(version: string) {
    return (
      docItems.find((doc) => doc.version === version && doc.locale === locale.value) ??
      docItems.find((doc) => doc.version === version && doc.locale === "en")
    );
  }

  function hydrateTheme() {
    const stored = localStorage.getItem("theme");
    isDark.value =
      stored === "dark" ||
      (!stored && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }

  function toggleTheme() {
    isDark.value = !isDark.value;
    localStorage.setItem("theme", isDark.value ? "dark" : "light");
  }

  return {
    locale,
    isDark,
    compareA,
    compareB,
    layers,
    versionMeta,
    versionOrder,
    allVersions,
    allDiffs,
    setLocale,
    t,
    versionLabel,
    getVersion,
    getDoc,
    hydrateTheme,
    toggleTheme,
  };
});
