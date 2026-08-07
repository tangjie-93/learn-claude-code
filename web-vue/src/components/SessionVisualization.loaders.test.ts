// @vitest-environment jsdom

import { describe, expect, it } from "vitest";
import { visualizationLoaders } from "./session-visualization-registry";

describe("SessionVisualization loaders", () => {
  it("loads registered visualization components on demand", async () => {
    const module = await visualizationLoaders.s01();

    expect(module.default).toBeTruthy();
    expect(Object.keys(visualizationLoaders)).toEqual([
      "s01",
      "s02",
      "s03",
      "s04",
      "s05",
      "s06",
      "s07",
      "s08",
      "s09",
      "s10",
      "s11",
      "s12",
      "s13",
      "s14",
      "s15",
      "s16",
      "s17",
      "s18",
      "s19",
      "s20",
    ]);
  });
});
