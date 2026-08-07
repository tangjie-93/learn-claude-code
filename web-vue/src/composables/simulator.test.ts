import { describe, expect, it, vi } from "vitest";
import { createSimulatorState } from "./simulator";

const steps = [
  { type: "user_message", content: "Ask", annotation: "user" },
  { type: "tool_call", content: "bash", annotation: "tool" },
  { type: "tool_result", content: "ok", annotation: "result" },
];

describe("createSimulatorState", () => {
  it("starts empty and advances one visible step at a time", () => {
    const sim = createSimulatorState(steps);

    expect(sim.visibleSteps.value).toEqual([]);
    sim.stepForward();
    expect(sim.currentIndex.value).toBe(1);
    expect(sim.visibleSteps.value.map((step) => step.content)).toEqual(["Ask"]);
  });

  it("reports completion when every step is visible", () => {
    const sim = createSimulatorState(steps);

    sim.stepForward();
    sim.stepForward();
    sim.stepForward();

    expect(sim.isComplete.value).toBe(true);
    expect(sim.visibleSteps.value).toHaveLength(3);
  });

  it("resets playback state", () => {
    const sim = createSimulatorState(steps);

    sim.stepForward();
    sim.play();
    sim.reset();

    expect(sim.currentIndex.value).toBe(0);
    expect(sim.visibleSteps.value).toEqual([]);
    expect(sim.isPlaying.value).toBe(false);
  });

  it("auto-plays using the configured speed", () => {
    vi.useFakeTimers();
    const sim = createSimulatorState(steps);

    sim.setSpeed(100);
    sim.play();
    vi.advanceTimersByTime(250);

    expect(sim.currentIndex.value).toBe(2);
    expect(sim.visibleSteps.value).toHaveLength(2);
    sim.pause();
    vi.useRealTimers();
  });
});
