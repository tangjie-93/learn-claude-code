import { describe, expect, it } from "vitest";
import { getEdgePath, getNodeMetrics } from "./flow-layout";
import type { FlowNode } from "@/types/agent-data";

const start: FlowNode = { id: "start", label: "Start", type: "start", x: 100, y: 40 };
const process: FlowNode = { id: "process", label: "Run Tool", type: "process", x: 100, y: 140 };
const decision: FlowNode = { id: "decision", label: "function_call?", type: "decision", x: 300, y: 140 };
const loopEnd: FlowNode = { id: "loop", label: "Append output", type: "process", x: 100, y: 320 };

describe("flow layout helpers", () => {
  it("sizes decision nodes differently from process nodes", () => {
    const processMetrics = getNodeMetrics(process);
    const decisionMetrics = getNodeMetrics(decision);

    expect(decisionMetrics.width).toBeGreaterThanOrEqual(92);
    expect(decisionMetrics.height).toBeGreaterThan(processMetrics.height);
  });

  it("creates a straight vertical path for aligned nodes", () => {
    const path = getEdgePath(start, process);

    expect(path).toMatch(/^M 100 \d+ L 100 \d+$/);
  });

  it("creates a curved horizontal path for side-by-side nodes", () => {
    const path = getEdgePath(process, decision);

    expect(path).toContain(" C ");
    expect(path).toMatch(/^M /);
  });

  it("routes backward edges around the graph", () => {
    const path = getEdgePath(loopEnd, start);

    expect(path).toContain(" C ");
    expect(path).toContain("-48");
  });
});
