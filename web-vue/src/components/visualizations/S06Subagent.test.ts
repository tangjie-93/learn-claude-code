// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import S06Subagent from "./S06Subagent.vue";

describe("S06Subagent", () => {
  it("renders isolated parent and child contexts and returns only a summary", async () => {
    const wrapper = mount(S06Subagent, {
      props: { title: "Subagent Context Isolation" },
    });

    expect(wrapper.text()).toContain("Subagent Context Isolation");
    expect(wrapper.text()).toContain("Parent Process");
    expect(wrapper.text()).toContain("Child Process");
    expect(wrapper.text()).toContain("user: Build login + tests");
    expect(wrapper.text()).toContain("messages[] (fresh)");
    expect(wrapper.text()).toContain("not yet spawned");
    expect(wrapper.text()).toContain("Parent Context");

    const next = wrapper.find('[title="Next step"]');

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("task: Write unit tests for auth");
    expect(wrapper.text()).toContain("task prompt");
    expect(wrapper.text()).toContain("Spawn Subagent");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("tool_use: read auth.ts");
    expect(wrapper.text()).toContain("tool_use: write test.ts");
    expect(wrapper.text()).toContain("Independent Work");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Compressing full context into summary...");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("summary");
    expect(wrapper.text()).toContain("context discarded");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("summary: 3 tests written, all passing");
    expect(wrapper.text()).toContain("3 original + 1 summary = clean context");
    expect(wrapper.text()).toContain("Clean Context");
  });
});
