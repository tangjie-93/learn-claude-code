// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S14CronScheduler from "./S14CronScheduler.vue";

describe("S14CronScheduler", () => {
  it("renders the cron schedule flow from schedule book to drained queue", async () => {
    const wrapper = mount(S14CronScheduler, {
      props: { title: "Cron Scheduler" },
    });

    expect(wrapper.text()).toContain("Cron Scheduler");
    expect(wrapper.text()).toContain("Weekly clock");
    expect(wrapper.text()).toContain("Schedule book");
    expect(wrapper.text()).toContain("Due queue");
    expect(wrapper.text()).toContain("Agent inbox");
    expect(wrapper.text()).toContain("Draft prompt");
    expect(wrapper.text()).toContain("no saved schedule yet");
    expect(wrapper.text()).toContain("08:59");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");

    expect(wrapper.text()).toContain("Store the Card");
    expect(wrapper.text()).toContain("0 9 * * 1-5");
    expect(wrapper.text()).toContain("stored schedules stay here");

    await next.trigger("click");

    expect(wrapper.text()).toContain("Time Keeps Moving");
    expect(wrapper.text()).toContain("09:00");
    expect(wrapper.get('[data-day="Wed"]').classes()).toContain("active-day");
    expect(wrapper.text()).toContain("watcher: running");

    await next.trigger("click");

    expect(wrapper.text()).toContain("Copy Goes to the Queue");
    expect(wrapper.text()).toContain("due copy");
    expect(wrapper.text()).toContain("same prompt, current timestamp");

    await next.trigger("click");

    expect(wrapper.text()).toContain("Run as a Normal Turn");
    expect(wrapper.text()).toContain("agent turn");
    expect(wrapper.text()).toContain("runs like a normal prompt");

    await next.trigger("click");

    expect(wrapper.text()).toContain("Keep the Original");
    expect(wrapper.text()).toContain("queue drained");
    expect(wrapper.text()).toContain("result appended");
    expect(wrapper.text()).toContain("review summary saved");
  });
});
