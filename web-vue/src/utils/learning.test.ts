import { describe, expect, it } from "vitest";
import versionsData from "@/data/generated/versions.json";
import { versionOrder } from "@/data/constants";
import {
  collectClassesForVersion,
  getLayerLegend,
  getLocGrowthRows,
  getVersionDiffSummary,
} from "./learning";
import type { VersionIndex } from "@/types/agent-data";

const data = versionsData as VersionIndex;

describe("learning data helpers", () => {
  it("builds a layer legend that covers every learning path version", () => {
    const legend = getLayerLegend();
    const covered = new Set(legend.flatMap((layer) => layer.versions));

    expect(legend.map((layer) => layer.id)).toEqual([
      "tools",
      "planning",
      "memory",
      "concurrency",
      "collaboration",
    ]);
    expect(versionOrder.every((version) => covered.has(version))).toBe(true);
  });

  it("computes LOC growth percentages from generated version data", () => {
    const rows = getLocGrowthRows(data.versions);

    expect(rows).toHaveLength(20);
    expect(rows[0]).toMatchObject({ id: "s01", loc: data.versions[0].loc });
    expect(rows.every((row) => row.percent >= 2 && row.percent <= 100)).toBe(true);
    expect(rows.at(-1)?.percent).toBe(100);
  });

  it("collects architecture classes with introduction metadata", () => {
    const classes = collectClassesForVersion(data, "s20");

    expect(classes.some((item) => item.name === "Task")).toBe(true);
    expect(classes.some((item) => item.name === "MCPClient")).toBe(true);
    expect(classes.find((item) => item.name === "Task")?.introducedIn).toBe("s12");
  });

  it("summarizes version diffs for deep dive panels", () => {
    const summary = getVersionDiffSummary(data, "s20");

    expect(summary).not.toBeNull();
    expect(summary?.to).toBe("s20");
    expect(summary?.locDelta).toBeGreaterThan(0);
    expect(summary?.newClasses).toContain("RecoveryState");
  });
});
