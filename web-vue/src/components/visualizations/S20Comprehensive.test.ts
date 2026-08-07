// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S20Comprehensive from "./S20Comprehensive.vue";

describe("S20Comprehensive", () => {
  it("walks through the complete agent turn from intake to transcript append", async () => {
    const wrapper = mount(S20Comprehensive, {
      props: { title: "Comprehensive Agent Turn" },
    });

    expect(wrapper.text()).toContain("Comprehensive Agent Turn");
    expect(wrapper.text()).toContain("One-turn journey");
    expect(wrapper.text()).toContain("Intake");
    expect(wrapper.text()).toContain("Turn packet");
    expect(wrapper.text()).toContain("Source-of-truth transcript");
    expect(wrapper.text()).toContain("background");
    expect(wrapper.text()).toContain("worktree");
    expect(wrapper.text()).toContain("A Turn Starts as a Packet");
    expect(wrapper.text()).toContain("memory and notes are attached");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    await next.trigger("click");
    await next.trigger("click");
    await next.trigger("click");

    expect(wrapper.text()).toContain("External Results Re-enter the Same Lane");
    expect(wrapper.text()).toContain("MCP tool name");
    expect(wrapper.find('[data-stage="external"]').text()).toContain("External");

    await next.trigger("click");
    await next.trigger("click");

    expect(wrapper.text()).toContain("Everything Writes Back to One Transcript");
    expect(wrapper.text()).toContain("final answer drafted");
    expect(wrapper.find('[data-stage="append"]').classes()).toContain("active");
  });
});
