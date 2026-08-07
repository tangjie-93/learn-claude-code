import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "./app";

describe("app store course data loading", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("starts without generated course data in state", () => {
    const app = useAppStore();

    expect(app.dataReady).toBe(false);
    expect(app.allVersions).toHaveLength(0);
    expect(app.getVersion("s01")).toBeUndefined();
  });

  it("loads generated versions and localized docs on demand", async () => {
    const app = useAppStore();

    await app.loadCourseData();

    expect(app.dataReady).toBe(true);
    expect(app.getVersion("s01")?.filename).toBe("s01_agent_loop/code_openai.py");
    expect(app.getDoc("s01")?.content).toContain("# s01:");
  });
});
