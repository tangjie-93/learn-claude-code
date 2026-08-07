// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import SessionVisualization from "./SessionVisualization.vue";

describe("SessionVisualization", () => {
  it("reserves a visualization host for registered versions", () => {
    const wrapper = mount(SessionVisualization, {
      props: { version: "s01", title: "The Agent Loop" },
      global: {
        stubs: { Transition: false },
      },
    });

    expect(wrapper.find('[data-testid="session-visualization-host"]').exists()).toBe(true);
  });

  it("does not render for unknown versions", () => {
    const wrapper = mount(SessionVisualization, {
      props: { version: "s99", title: "Unknown" },
    });

    expect(wrapper.find('[data-testid="session-visualization-host"]').exists()).toBe(false);
  });
});
