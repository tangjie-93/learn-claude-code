// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import S09Memory from "./S09Memory.vue";

describe("S09Memory", () => {
  it("renders memory sessions, catalog search, and selected memory injection across steps", async () => {
    const wrapper = mount(S09Memory, {
      props: { title: "Memory Library" },
    });

    expect(wrapper.text()).toContain("Memory Library");
    expect(wrapper.text()).toContain("Session A: learn");
    expect(wrapper.text()).toContain("Session B: recall");
    expect(wrapper.text()).toContain(".memory library");
    expect(wrapper.text()).toContain('"Please keep LCC pages concrete for beginners."');
    expect(wrapper.text()).toContain("future request has not arrived");
    expect(wrapper.text()).toContain("catalog has not been rebuilt yet");
    expect(wrapper.text()).toContain("A Fact Worth Keeping");

    const next = wrapper.find('[title="Next step"]');

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Memory extractor stamp");
    expect(wrapper.text()).toContain("Stamp It After the Turn");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Beginner visual preference");
    expect(wrapper.text()).toContain("lcc_visual_preference.md");
    expect(wrapper.text()).toContain("Write One Memory File");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("MEMORY.md catalog");
    expect(wrapper.text()).toContain("feedback");
    expect(wrapper.text()).toContain("Update the Catalog");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain('"Continue improving the web lesson visuals."');
    expect(wrapper.text()).toContain("LCC web paths");
    expect(wrapper.text()).toContain("A Future Request Arrives");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Catalog search selects");
    expect(wrapper.text()).toContain("selected");
    expect(wrapper.text()).toContain("Catalog Picks One");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Reading stack before LLM");
    expect(wrapper.text()).toContain("selected memory detail");
    expect(wrapper.text()).toContain("Build the Reading Stack");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("answer keeps the user's preference");
    expect(wrapper.text()).toContain("Continuity Without Clutter");
  });
});
