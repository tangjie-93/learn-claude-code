import { createRouter, createWebHistory, type RouteLocationNormalized } from "vue-router";
import { locales } from "@/data/constants";
import HomeView from "@/views/HomeView.vue";
import TimelineView from "@/views/TimelineView.vue";
import LayersView from "@/views/LayersView.vue";
import CompareView from "@/views/CompareView.vue";
import VersionView from "@/views/VersionView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/en" },
    { path: "/:locale(en|zh|ja)", name: "home", component: HomeView },
    { path: "/:locale(en|zh|ja)/timeline", name: "timeline", component: TimelineView },
    { path: "/:locale(en|zh|ja)/compare", name: "compare", component: CompareView },
    { path: "/:locale(en|zh|ja)/layers", name: "layers", component: LayersView },
    { path: "/:locale(en|zh|ja)/:version(s\\d{2})", name: "version", component: VersionView },
    { path: "/:pathMatch(.*)*", redirect: "/en" },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to: RouteLocationNormalized) => {
  const locale = String(to.params.locale || "");
  if (locale && !locales.includes(locale as never)) {
    return "/en";
  }
});

export default router;
