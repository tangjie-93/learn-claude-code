// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S12TaskSystem from "./S12TaskSystem.vue";

describe("S12TaskSystem", () => {
  it("renders task dependency lanes and unlocks dependent work", async () => {
    const wrapper = mount(S12TaskSystem, {
      props: { title: "Task Board Dependencies" },
    });

    expect(wrapper.text()).toContain("Task Board Dependencies");
    expect(wrapper.text()).toContain(".tasks board");
    expect(wrapper.text()).toContain("Waiting");
    expect(wrapper.text()).toContain("Ready");
    expect(wrapper.text()).toContain("Working");
    expect(wrapper.text()).toContain("Done");
    expect(wrapper.text()).toContain("T1");
    expect(wrapper.text()).toContain("Set up database");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    await next.trigger("click");
    await next.trigger("click");

    expect(wrapper.text()).toContain("Completion Unlocks Dependents");
    expect(wrapper.text()).toContain("Add API routes");
    expect(wrapper.find('[data-task="T2"]').classes()).toContain("ready");
  });
});
