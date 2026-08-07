// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S05TodoWrite from "./S05TodoWrite.vue";

describe("S05TodoWrite", () => {
  it("renders the TodoWrite kanban and advances through nag-driven task movement", async () => {
    const wrapper = mount(S05TodoWrite, {
      global: {
        stubs: { Transition: true },
      },
    });

    expect(wrapper.text()).toContain("TodoWrite Nag System");
    expect(wrapper.text()).toContain("The Plan");
    expect(wrapper.text()).toContain("Nag Timer");
    expect(wrapper.text()).toContain("0/3");
    expect(wrapper.text()).toContain("Pending");
    expect(wrapper.text()).toContain("In Progress");
    expect(wrapper.text()).toContain("Completed");
    expect(wrapper.text()).toContain("Write auth tests");
    expect(wrapper.text()).toContain("Fix mobile layout");
    expect(wrapper.text()).toContain("Progress: 0/4 complete");
    expect(wrapper.find('[data-testid="system-nag"]').exists()).toBe(false);

    const columns = () => wrapper.findAll("[data-testid='kanban-column']").map((column) => column.text());
    expect(columns()[0]).toContain("4");
    expect(columns()[1]).toContain("0");
    expect(columns()[2]).toContain("0");

    const next = wrapper.get('button[title="Next step"]');
    const advance = async () => {
      await next.trigger("click");
    };

    await advance();
    expect(wrapper.text()).toContain("Round 1 - Idle");
    expect(wrapper.text()).toContain("1/3");

    await advance();
    expect(wrapper.text()).toContain("Round 2 - Still Idle");
    expect(wrapper.text()).toContain("2/3");

    await advance();
    expect(wrapper.text()).toContain("NAG!");
    expect(wrapper.text()).toContain("3/3");
    expect(wrapper.get('[data-testid="system-nag"]').text()).toContain(
      'SYSTEM: "You have pending tasks. Pick one up now!"',
    );
    expect(columns()[0]).toContain("3");
    expect(columns()[1]).toContain("1");
    expect(columns()[1]).toContain("Write auth tests");

    await advance();
    expect(wrapper.text()).toContain("Task Complete");
    expect(wrapper.text()).toContain("Progress: 1/4 complete");
    expect(columns()[2]).toContain("Write auth tests");

    await advance();
    expect(wrapper.text()).toContain("Self-Directed");
    expect(columns()[1]).toContain("Fix mobile layout");

    await advance();
    expect(wrapper.text()).toContain("Mission Accomplished");
    expect(wrapper.text()).toContain("Progress: 3/4 complete");
    expect(columns()[1]).toContain("Update config loader");
    expect(columns()[2]).toContain("Add error handling");
  });

  it("uses an explicit title when provided", () => {
    const wrapper = mount(S05TodoWrite, {
      props: { title: "Custom TodoWrite" },
      global: {
        stubs: { Transition: true },
      },
    });

    expect(wrapper.text()).toContain("Custom TodoWrite");
    expect(wrapper.text()).not.toContain("TodoWrite Nag System");
  });
});
