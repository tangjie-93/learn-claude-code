import { describe, expect, it } from "vitest";
import { getDesignDecisions, getExecutionFlow } from "./deep-dive";

describe("deep dive helpers", () => {
  it("returns execution flow nodes and edges for a version", () => {
    const flow = getExecutionFlow("s01");

    expect(flow.nodes.length).toBeGreaterThan(0);
    expect(flow.edges.length).toBeGreaterThan(0);
    expect(flow.nodes[0]).toHaveProperty("label");
  });

  it("returns localized design decisions when available", () => {
    const decisions = getDesignDecisions("s01", "zh");

    expect(decisions.length).toBeGreaterThan(0);
    expect(decisions[0].title).toBeTruthy();
    expect(decisions[0]).toHaveProperty("description");
  });

  it("falls back to English decision text for unsupported locale fields", () => {
    const en = getDesignDecisions("s01", "en");
    const fallback = getDesignDecisions("s01", "unknown");

    expect(fallback[0].title).toBe(en[0].title);
  });
});
