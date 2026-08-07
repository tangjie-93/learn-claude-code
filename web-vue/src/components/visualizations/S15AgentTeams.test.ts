// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import S15AgentTeams from "./S15AgentTeams.vue";

describe("S15AgentTeams", () => {
  it("renders agent panels, mailbox cards, activity log, and step controls across the flow", async () => {
    const wrapper = mount(S15AgentTeams, {
      props: { title: "Team Mailbox Workbench" },
      global: {
        stubs: { TransitionGroup: true },
      },
    });

    expect(wrapper.text()).toContain("Team Mailbox Workbench");
    expect(wrapper.text()).toContain("Lead");
    expect(wrapper.text()).toContain("Coder");
    expect(wrapper.text()).toContain("Reviewer");
    expect(wrapper.text()).toContain("lead.jsonl");
    expect(wrapper.text()).toContain("coder.jsonl");
    expect(wrapper.text()).toContain("reviewer.jsonl");
    expect(wrapper.text()).toContain("What changed");
    expect(wrapper.text()).toContain("team config creates lead, coder, reviewer");
    expect(wrapper.text()).toContain("A Team Is Mailboxes");
    expect(wrapper.find('[data-mail="assign"]').exists()).toBe(false);

    const next = wrapper.get('button[title="Next step"]');

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Lead Drops a Card");
    expect(wrapper.text()).toContain("Build login UI");
    expect(wrapper.find('[data-mail="assign"]').exists()).toBe(true);
    expect(wrapper.find(".agent-panel.working").text()).toContain("Lead");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Coder Reads Before Thinking");
    expect(wrapper.find('[data-mail="assign"]').exists()).toBe(false);
    expect(wrapper.find(".agent-panel.reading").text()).toContain("Coder");

    await next.trigger("click");
    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Result Becomes Mail");
    expect(wrapper.text()).toContain("Login UI done");
    expect(wrapper.find('[data-mail="result"]').exists()).toBe(true);

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Reviewer Sends Feedback");
    expect(wrapper.text()).toContain("Review passed");
    expect(wrapper.find('[data-mail="feedback"]').exists()).toBe(true);
    expect(wrapper.find('[data-mail="result"]').exists()).toBe(false);
    expect(wrapper.text()).toContain("reviewer appends feedback to lead.jsonl");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Files Are the Coordination Layer");
    expect(wrapper.findAll(".agent-panel.done")).toHaveLength(2);
    expect(wrapper.text()).toContain("all coordination remains visible on disk");
  });
});
