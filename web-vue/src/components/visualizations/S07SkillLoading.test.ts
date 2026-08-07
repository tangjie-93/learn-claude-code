// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S07SkillLoading from "./S07SkillLoading.vue";

describe("S07SkillLoading", () => {
  it("shows the skill catalog, token count, on-demand injection, and step controls", async () => {
    const wrapper = mount(S07SkillLoading, {
      props: { title: "On-Demand Skill Loading" },
      global: {
        stubs: { Transition: true, TransitionGroup: true },
      },
    });

    expect(wrapper.text()).toContain("On-Demand Skill Loading");
    expect(wrapper.text()).toContain("# Available Skills");
    expect(wrapper.text()).toContain("/commit");
    expect(wrapper.text()).toContain("/review-pr");
    expect(wrapper.text()).toContain("/test");
    expect(wrapper.text()).toContain("/deploy");
    expect(wrapper.text()).toContain("Tokens");
    expect(wrapper.text()).toContain("120");
    expect(wrapper.text()).toContain("Layer 1: Compact Summaries");

    const next = wrapper.get('button[title="Next step"]');

    await next.trigger("click");
    expect(wrapper.text()).toContain("User types:");
    expect(wrapper.text()).toContain("Skill Invocation");

    await next.trigger("click");
    expect(wrapper.text()).toContain("SKILL.md: /commit");
    expect(wrapper.text()).toContain("tool_result");
    expect(wrapper.text()).toContain("Run git status + git diff to see changes");
    expect(wrapper.text()).toContain("440");
    expect(wrapper.text()).toContain("Layer 2: Full Injection");

    await next.trigger("click");
    expect(wrapper.text()).toContain("The Skill tool returns content as a tool_result message.");
    expect(wrapper.text()).toContain("In Context Now");

    await next.trigger("click");
    expect(wrapper.text()).toContain("SKILL.md: /review-pr");
    expect(wrapper.text()).toContain("Fetch PR diff via gh pr view");
    expect(wrapper.text()).toContain("780");
    expect(wrapper.text()).toContain("Stack Skills");

    await next.trigger("click");
    expect(wrapper.text()).toContain("LAYER 1");
    expect(wrapper.text()).toContain("Always present, ~120 tokens");
    expect(wrapper.text()).toContain("LAYER 2");
    expect(wrapper.text()).toContain("On demand, ~300-500 tokens each");
    expect(wrapper.text()).toContain("Two-Layer Architecture");
  });
});
