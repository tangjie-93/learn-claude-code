import { createRouter, createWebHistory, type RouteLocationNormalized } from "vue-router";
import { locales } from "@/data/constants";
import { useAppStore } from "@/stores/app";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/en" },
    { path: "/:locale(en|zh|ja)", name: "home", component: () => import("@/views/HomeView.vue") },
    { path: "/:locale(en|zh|ja)/timeline", name: "timeline", component: () => import("@/views/TimelineView.vue") },
    { path: "/:locale(en|zh|ja)/compare", name: "compare", component: () => import("@/views/CompareView.vue") },
    { path: "/:locale(en|zh|ja)/layers", name: "layers", component: () => import("@/views/LayersView.vue") },
    { path: "/:locale(en|zh|ja)/:version(s\\d{2})", name: "version", component: () => import("@/views/VersionView.vue") },
    { path: "/:pathMatch(.*)*", redirect: "/en" },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach(async (to: RouteLocationNormalized) => {
  const locale = String(to.params.locale || "");
  if (locale && !locales.includes(locale as never)) {
    return "/en";
  }
  const app = useAppStore();
  app.setLocale(locale || "en");
  await app.loadCourseData();
});

export default router;
