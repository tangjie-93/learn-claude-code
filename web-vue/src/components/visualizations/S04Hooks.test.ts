// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S04Hooks from "./S04Hooks.vue";

describe("S04Hooks", () => {
  it("renders the hook registry and advances through hook events", async () => {
    const wrapper = mount(S04Hooks, {
      props: { title: "Hooks" },
    });

    expect(wrapper.text()).toContain("Hooks");
    expect(wrapper.text()).toContain("Hook registry");
    expect(wrapper.text()).toContain("UserPromptSubmit");
    expect(wrapper.text()).toContain("PreToolUse");
    expect(wrapper.text()).toContain("trigger_hooks(event)");

    await wrapper.find('[title="Next step"]').trigger("click");
    await wrapper.find('[title="Next step"]').trigger("click");
    await wrapper.find('[title="Next step"]').trigger("click");

    expect(wrapper.text()).toContain("Permission and logging hooks run before the handler");
    expect(wrapper.find('[data-hook="PreToolUse"]').classes()).toContain("active");
  });
});
