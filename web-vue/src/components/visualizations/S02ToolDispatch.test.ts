// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import S02ToolDispatch from "./S02ToolDispatch.vue";

describe("S02ToolDispatch", () => {
  it("renders the tool dispatch map and advances routed requests", async () => {
    const wrapper = mount(S02ToolDispatch, {
      props: { title: "Tool Dispatch Map" },
    });

    expect(wrapper.text()).toContain("Tool Dispatch Map");
    expect(wrapper.text()).toContain("Incoming:");
    expect(wrapper.text()).toContain("waiting for tool_call...");
    expect(wrapper.text()).toContain("dispatch(name)");
    expect(wrapper.text()).toContain("bash");
    expect(wrapper.text()).toContain("read_file");
    expect(wrapper.text()).toContain("write_file");
    expect(wrapper.text()).toContain("edit_file");
    expect(wrapper.text()).toMatch(/const handlers = \{.*bash,.*read_file,.*write_file,.*edit_file,.*\}/);
    expect(wrapper.text()).toContain("The Dispatch Map");

    await wrapper.find('[data-testid="step-next"]').trigger("click");
    await nextTick();

    expect(wrapper.text()).toContain('{ name: "bash", input: { cmd: "ls -la" } }');
    expect(wrapper.text()).toContain("Route: bash");
    expect(wrapper.find('[data-tool="bash"]').classes()).toContain("is-active");
  });
});
