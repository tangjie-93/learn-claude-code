// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S11ErrorRecovery from "./S11ErrorRecovery.vue";

describe("S11ErrorRecovery", () => {
  it("renders bounded recovery paths and advances through provider failures", async () => {
    const wrapper = mount(S11ErrorRecovery, {
      props: { title: "Error Recovery Paths" },
    });

    expect(wrapper.text()).toContain("Error Recovery Paths");
    expect(wrapper.text()).toContain("max_tokens");
    expect(wrapper.text()).toContain("prompt_too_long");
    expect(wrapper.text()).toContain("429");
    expect(wrapper.text()).toContain("529");
    expect(wrapper.text()).toContain("Normal Call Still Comes First");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("8K -> 64K");
    expect(wrapper.find('[data-case="max-tokens"]').classes()).toContain("active");

    await next.trigger("click");
    expect(wrapper.text()).toContain("reactive_compact(messages)");

    await next.trigger("click");
    expect(wrapper.text()).toContain("backoff + jitter");

    await next.trigger("click");
    expect(wrapper.text()).toContain("fallback model");
  });
});
