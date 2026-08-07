import { describe, expect, it } from "vitest";
import versions from "@/data/generated/versions.json";
import { buildVersionComparison } from "./compare";
import type { VersionIndex } from "@/types/agent-data";

const data = versions as VersionIndex;

describe("buildVersionComparison", () => {
  it("returns null when either version is missing", () => {
    expect(buildVersionComparison(data, "", "s02")).toBeNull();
    expect(buildVersionComparison(data, "s01", "missing")).toBeNull();
  });

  it("computes structural differences between two versions", () => {
    const comparison = buildVersionComparison(data, "s01", "s02");

    expect(comparison).not.toBeNull();
    expect(comparison?.locDelta).toBeGreaterThan(0);
    expect(comparison?.toolsOnlyB).toContain("read_file");
    expect(comparison?.toolsShared).toContain("bash");
  });

  it("exposes side-by-side source metadata for code diff views", () => {
    const comparison = buildVersionComparison(data, "s19", "s20");

    expect(comparison?.left.filename).toContain("s19");
    expect(comparison?.right.filename).toContain("s20");
    expect(comparison?.left.source.length).toBeGreaterThan(100);
    expect(comparison?.right.source.length).toBeGreaterThan(100);
  });
});
