// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { defineComponent, nextTick } from "vue";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useSteppedVisualization } from "./stepped-visualization";

function mountHarness(totalSteps = 3, autoPlayInterval = 100) {
  return mount(
    defineComponent({
      setup() {
        return useSteppedVisualization({ totalSteps, autoPlayInterval });
      },
      template: `
        <div>
          <output data-testid="step">{{ currentStep }}</output>
          <output data-testid="playing">{{ isPlaying }}</output>
          <button data-testid="next" @click="next">next</button>
          <button data-testid="prev" @click="prev">prev</button>
          <button data-testid="reset" @click="reset">reset</button>
          <button data-testid="toggle" @click="toggleAutoPlay">toggle</button>
        </div>
      `,
    })
  );
}

function mountHarnessAt(initialStep: number, totalSteps = 3) {
  return mount(
    defineComponent({
      setup() {
        return useSteppedVisualization({ totalSteps, initialStep });
      },
      template: `<output data-testid="step">{{ currentStep }}</output>`,
    })
  );
}

describe("useSteppedVisualization", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("moves between steps without exceeding the first or last step", async () => {
    const wrapper = mountHarness();

    await wrapper.find('[data-testid="prev"]').trigger("click");
    expect(wrapper.find('[data-testid="step"]').text()).toBe("0");

    await wrapper.find('[data-testid="next"]').trigger("click");
    await wrapper.find('[data-testid="next"]').trigger("click");
    await wrapper.find('[data-testid="next"]').trigger("click");

    expect(wrapper.find('[data-testid="step"]').text()).toBe("2");
  });

  it("auto-plays until the last step and then stops", async () => {
    vi.useFakeTimers();
    const wrapper = mountHarness(3, 100);

    await wrapper.find('[data-testid="toggle"]').trigger("click");
    expect(wrapper.find('[data-testid="playing"]').text()).toBe("true");

    vi.advanceTimersByTime(100);
    await nextTick();
    vi.advanceTimersByTime(100);
    await nextTick();
    vi.advanceTimersByTime(100);
    await nextTick();

    expect(wrapper.find('[data-testid="step"]').text()).toBe("2");
    expect(wrapper.find('[data-testid="playing"]').text()).toBe("false");
  });

  it("reset returns to the first step and stops playback", async () => {
    const wrapper = mountHarness();

    await wrapper.find('[data-testid="next"]').trigger("click");
    await wrapper.find('[data-testid="toggle"]').trigger("click");
    await wrapper.find('[data-testid="reset"]').trigger("click");

    expect(wrapper.find('[data-testid="step"]').text()).toBe("0");
    expect(wrapper.find('[data-testid="playing"]').text()).toBe("false");
  });

  it("can start at a clamped initial step", () => {
    expect(mountHarnessAt(2).find('[data-testid="step"]').text()).toBe("2");
    expect(mountHarnessAt(9).find('[data-testid="step"]').text()).toBe("2");
    expect(mountHarnessAt(-1).find('[data-testid="step"]').text()).toBe("0");
  });
});
