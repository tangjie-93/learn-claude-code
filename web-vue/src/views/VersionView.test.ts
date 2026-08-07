// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { RouterLinkStub } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { describe, expect, it } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";
import VersionView from "./VersionView.vue";
import { useAppStore } from "@/stores/app";

async function mountVersionView() {
  const pinia = createPinia();
  setActivePinia(pinia);
  const app = useAppStore();
  await app.loadCourseData();

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: "/:locale(en|zh|ja)/:version(s\\d{2})", component: VersionView }],
  });
  await router.push("/en/s01");
  await router.isReady();

  return mount(VersionView, {
    global: {
      plugins: [pinia, router],
      stubs: {
        RouterLink: RouterLinkStub,
        AppSidebar: true,
        MarkdownBlock: true,
        SimulatorPanel: true,
        SourcePanel: true,
        ExecutionFlowPanel: true,
        ArchitecturePanel: true,
        WhatsNewPanel: true,
        DesignDecisionsPanel: true,
        SessionVisualization: {
          props: ["version"],
          template: '<section data-testid="session-visualization">{{ version }}</section>',
        },
      },
    },
  });
}

describe("VersionView", () => {
  it("renders the session visualization before tabbed content", async () => {
    const wrapper = await mountVersionView();

    const html = wrapper.html();
    const visualizationIndex = html.indexOf('data-testid="session-visualization"');
    const tabsIndex = html.indexOf('class="tabs"');

    expect(visualizationIndex).toBeGreaterThan(-1);
    expect(tabsIndex).toBeGreaterThan(-1);
    expect(visualizationIndex).toBeLessThan(tabsIndex);
  });
});
