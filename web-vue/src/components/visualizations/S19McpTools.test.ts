// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S19McpTools from "./S19McpTools.vue";

describe("S19McpTools", () => {
  it("shows MCP tools moving from an external server onto the agent tool belt", async () => {
    const wrapper = mount(S19McpTools, {
      props: { title: "MCP Tool Bridge" },
    });

    expect(wrapper.text()).toContain("MCP Tool Bridge");
    expect(wrapper.text()).toContain("Built-in belt");
    expect(wrapper.text()).toContain("read_file");
    expect(wrapper.text()).toContain("External toolbox");
    expect(wrapper.text()).toContain("docs-server");
    expect(wrapper.text()).toContain("offline");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("connected");

    await next.trigger("click");
    expect(wrapper.text()).toContain("search");
    expect(wrapper.text()).toContain("fetch");

    await next.trigger("click");
    expect(wrapper.text()).toContain("mcp__docs__search");

    await next.trigger("click");
    expect(wrapper.text()).toContain("mcp__docs__search({ query })");

    await next.trigger("click");
    expect(wrapper.text()).toContain("tool_result: 3 relevant docs found");
  });
});
