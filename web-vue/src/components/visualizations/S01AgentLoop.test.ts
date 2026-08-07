// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S01AgentLoop from "./S01AgentLoop.vue";

describe("S01AgentLoop", () => {
  it("renders the agent loop title and core while-loop label", () => {
    const wrapper = mount(S01AgentLoop, {
      props: { title: "The Agent Loop" },
    });

    expect(wrapper.find('[data-testid="session-visualization"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("The Agent Loop");
    expect(wrapper.text()).toContain("while");
  });
});
