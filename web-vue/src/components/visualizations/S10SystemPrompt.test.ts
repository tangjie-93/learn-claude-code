// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { nextTick } from "vue";
import S10SystemPrompt from "./S10SystemPrompt.vue";

describe("S10SystemPrompt", () => {
  it("renders runtime prompt assembly and advances through cache states", async () => {
    const wrapper = mount(S10SystemPrompt, {
      props: { title: "Runtime Prompt Assembly" },
    });

    expect(wrapper.text()).toContain("Runtime Prompt Assembly");
    expect(wrapper.text()).toContain("Runtime context");
    expect(wrapper.text()).toContain("workspace");
    expect(wrapper.text()).toContain("/repo");
    expect(wrapper.text()).toContain("tools");
    expect(wrapper.text()).toContain("bash, read_file");
    expect(wrapper.text()).toContain("memory");
    expect(wrapper.text()).toContain("enabled");
    expect(wrapper.text()).toContain("skills");
    expect(wrapper.text()).toContain("code-review");
    expect(wrapper.text()).toContain("Section shelf + cache");
    expect(wrapper.text()).toContain("identity");
    expect(wrapper.text()).toContain("owner: core");
    expect(wrapper.text()).toContain("context key");
    expect(wrapper.text()).toContain("json.dumps(context, sort_keys=True)");
    expect(wrapper.text()).toContain("waiting for state");
    expect(wrapper.text()).toContain("System prompt");
    expect(wrapper.text()).toContain("prompt not built yet");
    expect(wrapper.text()).toContain("Runtime State Arrives");

    const next = wrapper.find('[title="Next step"]');

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Section Shelf Selects Owners");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Context Key Checks the Cache");
    expect(wrapper.text()).toContain("cache miss: assemble sections");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Prompt Is Assembled");
    expect(wrapper.text()).toContain("[identity]");
    expect(wrapper.text()).toContain("system prompt ready");
    expect(wrapper.text()).toContain("Traceable prompt text, assembled from named runtime owners.");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("Same Key Reuses the Prompt");
    expect(wrapper.text()).toContain("cache hit: reuse prompt");

    await next.trigger("click");
    await nextTick();
    expect(wrapper.text()).toContain("LLM Sees the Built Prompt");
    expect(wrapper.text()).toContain("sent to LLM");
    expect(wrapper.text()).toContain(
      "Beginner rule: system prompts should be assembled from named runtime facts, then cached only when those facts are unchanged.",
    );
  });
});
