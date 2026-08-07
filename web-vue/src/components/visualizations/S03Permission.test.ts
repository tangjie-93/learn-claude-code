// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S03Permission from "./S03Permission.vue";

describe("S03Permission", () => {
  it("renders the permission desk overview and advances through every route", async () => {
    const wrapper = mount(S03Permission, {
      props: { title: "Permission Desk" },
      global: {
        stubs: { Transition: true },
      },
    });

    expect(wrapper.text()).toContain("Permission Desk");
    expect(wrapper.text()).toContain("Three Requests, Three Routes");
    expect(wrapper.text()).toContain("read_file");
    expect(wrapper.text()).toContain("rm -rf ./tmp/build-cache");
    expect(wrapper.text()).toContain("sudo rm -rf /");
    expect(wrapper.text()).toContain("select a request route");

    const next = wrapper.get('button[title="Next step"]');
    const advance = async () => {
      await next.trigger("click");
    };

    await advance();
    expect(wrapper.text()).toContain("Allow: Safe Read Runs Immediately");
    expect(wrapper.text()).toContain("Handler runs now");
    expect(wrapper.text()).toContain('path: "README.md"');

    await advance();
    expect(wrapper.text()).toContain("Ask: Risky Local Delete Becomes a Ticket");
    expect(wrapper.text()).toContain("Approval ticket");
    expect(wrapper.text()).toContain('"Allow deleting local build cache?"');

    await advance();
    expect(wrapper.text()).toContain("Approved Ask: Handler Runs After Yes");
    expect(wrapper.text()).toContain("Handler runs after approval");

    await advance();
    expect(wrapper.text()).toContain("Deny: Forbidden Pattern Stops Early");
    expect(wrapper.text()).toContain("Blocked before handler");
    expect(wrapper.text()).toContain("No tool execution, no user prompt, no filesystem touch.");

    await advance();
    expect(wrapper.text()).toContain("One Permission Desk, Three Outcomes");
    expect(wrapper.text()).toContain("decision returned to loop");
    expect(wrapper.text()).toContain("Permission stays outside the model");
  });
});
