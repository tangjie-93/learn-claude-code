// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S16TeamProtocols from "./S16TeamProtocols.vue";

describe("S16TeamProtocols", () => {
  it("renders shutdown protocol cards and advances through the clean-exit flow", async () => {
    const wrapper = mount(S16TeamProtocols, {
      props: { title: "Team Protocol Cards" },
    });

    expect(wrapper.text()).toContain("Team Protocol Cards");
    expect(wrapper.text()).toContain("Shutdown");
    expect(wrapper.text()).toContain("Plan Approval");
    expect(wrapper.text()).toContain("Protocol state");
    expect(wrapper.text()).toContain("request_id: req_abc");
    expect(wrapper.text()).toContain("Leader desk");
    expect(wrapper.text()).toContain("Shared card shape");
    expect(wrapper.text()).toContain("Teammate desk");
    expect(wrapper.text()).toContain("Agree on a Small Form");
    expect(wrapper.text()).toContain("waiting for a protocol card");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("Leader Files a Request");
    expect(wrapper.text()).toContain("shutdown_request");
    expect(wrapper.text()).toContain("mode: polite");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Teammate Chooses");
    expect(wrapper.text()).toContain("decision card");
    expect(wrapper.text()).toContain("state: deciding");

    await next.trigger("click");
    expect(wrapper.text()).toContain("Clean Exit");
    expect(wrapper.text()).toContain("shutdown_response");
    expect(wrapper.text()).toContain("state: exited");
    expect(wrapper.text()).toContain("status: closed");
  });

  it("switches to plan approval and resets the stepped controls", async () => {
    const wrapper = mount(S16TeamProtocols);

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("shutdown_request");

    await wrapper.get('[data-protocol="plan"]').trigger("click");

    expect(wrapper.text()).toContain("Work Is Locked");
    expect(wrapper.text()).toContain("draft plan not submitted");
    expect(wrapper.text()).toContain("implementation locked until approval");
    expect(wrapper.text()).not.toContain("shutdown_request");

    await wrapper.get('button[title="Next step"]').trigger("click");
    expect(wrapper.text()).toContain("Submit the Plan Card");
    expect(wrapper.text()).toContain("exit_plan_mode");
    expect(wrapper.text()).toContain("1. edit module");

    await wrapper.get('button[title="Next step"]').trigger("click");
    expect(wrapper.text()).toContain("Approval Unlocks Action");
    expect(wrapper.text()).toContain("plan_approval_response");
    expect(wrapper.text()).toContain("unlock: implementation");
  });
});
