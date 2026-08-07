// @vitest-environment jsdom

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import S18WorktreeIsolation from "./S18WorktreeIsolation.vue";

describe("S18WorktreeIsolation", () => {
  it("renders task-to-worktree lanes and isolated execution directories", async () => {
    const wrapper = mount(S18WorktreeIsolation, {
      props: { title: "Worktree Task Isolation" },
    });

    expect(wrapper.text()).toContain("Worktree Task Isolation");
    expect(wrapper.text()).toContain("Task Board");
    expect(wrapper.text()).toContain("Worktree Index");
    expect(wrapper.text()).toContain("Execution Lanes");
    expect(wrapper.text()).toContain("Single Workspace Pain");

    const next = wrapper.get('button[title="Next step"]');
    await next.trigger("click");
    expect(wrapper.text()).toContain("auth-refactor");
    expect(wrapper.find('[data-worktree="auth-refactor"]').exists()).toBe(true);

    await next.trigger("click");
    expect(wrapper.text()).toContain("ui-login");
    expect(wrapper.find('[data-lane="wt/ui-login"]').text()).toContain("ui/Login.tsx");
  });
});
