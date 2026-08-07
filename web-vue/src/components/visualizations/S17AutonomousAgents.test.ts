// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S17AutonomousAgents from "./S17AutonomousAgents.vue";

describe("S17AutonomousAgents", () => {
  it("renders autonomous agents claiming visible board tasks", async () => {
    const wrapper = mount(S17AutonomousAgents, {
      props: { title: "Autonomous Work Board" },
    });

    expect(wrapper.text()).toContain("Autonomous Work Board");
    expect(wrapper.text()).toContain("Agent A");
    expect(wrapper.text()).toContain("Shared task board");
    expect(wrapper.text()).toContain("Fix auth bug");
    expect(wrapper.text()).toContain("Quiet Agents");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    await next.trigger("click");
    await next.trigger("click");

    expect(wrapper.text()).toContain("Claim One Card");
    expect(wrapper.find('[data-agent="A"]').text()).toContain("claiming");
    expect(wrapper.find('[data-task="T1"]').text()).toContain("owner: A");
  });
});
