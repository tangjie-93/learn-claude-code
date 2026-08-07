// @vitest-environment jsdom

import { mount, RouterLinkStub } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";
import AppHeader from "./AppHeader.vue";

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: "/:locale(en|zh|ja)?", component: { template: "<div />" } }],
  });
}

describe("AppHeader mobile menu", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("keeps mobile menu hidden until the menu button is clicked", async () => {
    const wrapper = mount(AppHeader, {
      global: {
        plugins: [makeRouter()],
        stubs: { RouterLink: RouterLinkStub },
      },
    });

    expect(wrapper.find('[data-testid="mobile-menu"]').exists()).toBe(false);
    await wrapper.find('[data-testid="mobile-menu-button"]').trigger("click");
    expect(wrapper.find('[data-testid="mobile-menu"]').exists()).toBe(true);
  });

  it("closes mobile menu after clicking a navigation link", async () => {
    const wrapper = mount(AppHeader, {
      global: {
        plugins: [makeRouter()],
        stubs: { RouterLink: RouterLinkStub },
      },
    });

    await wrapper.find('[data-testid="mobile-menu-button"]').trigger("click");
    await wrapper.find('[data-testid="mobile-menu"] a').trigger("click");

    expect(wrapper.find('[data-testid="mobile-menu"]').exists()).toBe(false);
  });

  it("switches locale by preserving the current path shape", async () => {
    const router = makeRouter();
    await router.push("/en");
    const push = vi.spyOn(router, "push");
    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router],
        stubs: { RouterLink: RouterLinkStub },
      },
    });

    const zhButton = wrapper.findAll(".locale-tabs button").find((button) => button.text() === "中文");
    expect(zhButton).toBeTruthy();
    await zhButton?.trigger("click");

    expect(push).toHaveBeenCalledWith("/zh");
  });
});
