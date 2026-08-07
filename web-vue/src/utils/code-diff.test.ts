import { describe, expect, it } from "vitest";
import { buildSplitDiffRows, buildUnifiedDiffRows } from "./code-diff";

describe("code diff helpers", () => {
  it("builds unified rows with old and new line numbers", () => {
    const rows = buildUnifiedDiffRows("a\nb\nc\n", "a\nB\nc\nd\n");

    expect(rows.map((row) => row.type)).toEqual(["context", "remove", "add", "context", "add"]);
    expect(rows.find((row) => row.type === "remove")).toMatchObject({ oldNum: 2, newNum: null, text: "b" });
    expect(rows.at(-1)).toMatchObject({ oldNum: null, newNum: 4, text: "d" });
  });

  it("preserves empty lines like the original diff view", () => {
    const rows = buildUnifiedDiffRows("a\n\nb\n", "a\n\nB\n");

    expect(rows.map((row) => row.text)).toEqual(["a", "", "b", "B"]);
    expect(rows[1]).toMatchObject({ oldNum: 2, newNum: 2, type: "context", text: "" });
  });

  it("builds split rows pairing replacements side by side", () => {
    const rows = buildSplitDiffRows("a\nb\n", "a\nB\n");

    expect(rows).toHaveLength(2);
    expect(rows[1].left).toMatchObject({ num: 2, text: "b", type: "remove" });
    expect(rows[1].right).toMatchObject({ num: 2, text: "B", type: "add" });
  });
});
