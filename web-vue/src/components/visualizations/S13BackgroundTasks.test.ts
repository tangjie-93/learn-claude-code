// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S13BackgroundTasks from "./S13BackgroundTasks.vue";

describe("S13BackgroundTasks", () => {
  it("renders background task lanes and drains queued notifications before the next LLM call", async () => {
    const wrapper = mount(S13BackgroundTasks, {
      props: { title: "Background Task Lanes" },
    });

    expect(wrapper.text()).toContain("Background Task Lanes");
    expect(wrapper.text()).toContain("Main Thread");
    expect(wrapper.text()).toContain("Background 1");
    expect(wrapper.text()).toContain("Background 2");
    expect(wrapper.text()).toContain("Notification");
    expect(wrapper.text()).toContain("Queue");
    expect(wrapper.text()).toContain("Three Lanes");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("The main agent loop runs as usual");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Main agent loop");
    expect(wrapper.text()).toContain("Background tasks run as daemon threads");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Multiple background tasks can run concurrently");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Lint code");
    expect(wrapper.text()).toContain("Lint: 0 errors");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Run tests");
    expect(wrapper.text()).toContain("Tests: 42 passed");
    expect(wrapper.text()).toContain("LLM API call");

    await next.trigger("click");
    expect(wrapper.text()).toContain("queue drained -- injected into next LLM call");
    expect(wrapper.text()).toContain("Drain Queue");
    expect(wrapper.text()).toContain("7/7");
  });
});
