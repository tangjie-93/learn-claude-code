// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S08ContextCompact from "./S08ContextCompact.vue";

describe("S08ContextCompact", () => {
  it("renders context compression stages and advances through the compacting flow", async () => {
    const wrapper = mount(S08ContextCompact, {
      global: {
        stubs: { Transition: true, TransitionGroup: true },
      },
    });

    expect(wrapper.text()).toContain("Three-Layer Context Compression");
    expect(wrapper.text()).toContain("Context Window");
    expect(wrapper.text()).toContain("Token usage");
    expect(wrapper.text()).toContain("30,000 / 100,000");
    expect(wrapper.text()).toContain("30%");
    expect(wrapper.text()).toContain("user");
    expect(wrapper.text()).toContain("assistant");
    expect(wrapper.text()).toContain("tool_result");
    expect(wrapper.text()).toContain("Micro");
    expect(wrapper.text()).toContain("Auto");
    expect(wrapper.text()).toContain("Manual");
    expect(wrapper.text()).toContain("Growing Context");

    const next = wrapper.get('button[title="Next step"]');
    const advance = async () => {
      await next.trigger("click");
    };

    await advance();
    expect(wrapper.text()).toContain("60,000 / 100,000");
    expect(wrapper.text()).toContain("Context Growing");

    await advance();
    expect(wrapper.text()).toContain("80,000 / 100,000");
    expect(wrapper.text()).toContain("tool_results are the largest blocks");
    expect(wrapper.text()).toContain("Approaching Limit");

    await advance();
    expect(wrapper.text()).toContain("MICRO-COMPACT");
    expect(wrapper.text()).toContain("Old tool_results shrunk to tiny summaries");

    await advance();
    expect(wrapper.text()).toContain("85,000 / 100,000");
    expect(wrapper.text()).toContain("Still Growing");

    await advance();
    expect(wrapper.text()).toContain("AUTO-COMPACT");
    expect(wrapper.text()).toContain("Full conversation compressed to summary block");
    expect(wrapper.text()).toContain("SUMMARY");

    await advance();
    expect(wrapper.text()).toContain("/compact");
    expect(wrapper.text()).toContain("COMPACT SUMMARY");
    expect(wrapper.text()).toContain("Stage 1: Micro -- shrink bulky outputs");
    expect(wrapper.text()).toContain("Stage 2: Auto -- summarize the conversation");
    expect(wrapper.text()).toContain("Stage 3: Manual -- keep one compact summary");
  });

  it("uses an explicit title when provided", () => {
    const wrapper = mount(S08ContextCompact, {
      props: { title: "Custom Context Compression" },
      global: {
        stubs: { Transition: true, TransitionGroup: true },
      },
    });

    expect(wrapper.text()).toContain("Custom Context Compression");
    expect(wrapper.text()).not.toContain("Three-Layer Context Compression");
  });
});
