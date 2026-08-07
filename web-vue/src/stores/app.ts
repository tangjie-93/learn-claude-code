import { defineStore } from "pinia";
import { computed, ref } from "vue";
import en from "@/i18n/messages/en.json";
import zh from "@/i18n/messages/zh.json";
import ja from "@/i18n/messages/ja.json";
import { layers, locales, versionMeta, versionOrder, type Locale } from "@/data/constants";
import type { DocContent, VersionIndex } from "@/types/agent-data";

const messages = { en, zh, ja } as const;
const emptyVersionIndex: VersionIndex = { versions: [], diffs: [] };

let courseDataPromise: Promise<void> | undefined;

export const useAppStore = defineStore("app", () => {
  const locale = ref<Locale>("en");
  const isDark = ref(false);
  const compareA = ref("");
  const compareB = ref("");
  const versionIndex = ref<VersionIndex>(emptyVersionIndex);
  const docItems = ref<DocContent[]>([]);
  const dataReady = ref(false);

  const allVersions = computed(() => versionIndex.value.versions);
  const allDiffs = computed(() => versionIndex.value.diffs);

  async function loadCourseData() {
    if (dataReady.value) {
      return;
    }
    courseDataPromise ??= Promise.all([
      import("@/data/generated/versions.json"),
      import("@/data/generated/docs.json"),
    ]).then(([versionsModule, docsModule]) => {
      versionIndex.value = versionsModule.default as VersionIndex;
      docItems.value = docsModule.default as DocContent[];
      dataReady.value = true;
    });
    await courseDataPromise;
  }

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
    return versionIndex.value.versions.find((version) => version.id === id);
  }

  function getDoc(version: string) {
    return (
      docItems.value.find((doc) => doc.version === version && doc.locale === locale.value) ??
      docItems.value.find((doc) => doc.version === version && doc.locale === "en")
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
    dataReady,
    layers,
    versionMeta,
    versionOrder,
    allVersions,
    allDiffs,
    loadCourseData,
    setLocale,
    t,
    versionLabel,
    getVersion,
    getDoc,
    hydrateTheme,
    toggleTheme,
  };
});
