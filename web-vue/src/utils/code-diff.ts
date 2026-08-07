import { diffLines } from "diff";

export type UnifiedDiffRow = {
  oldNum: number | null;
  newNum: number | null;
  type: "add" | "remove" | "context";
  text: string;
};

export type SplitDiffCell = {
  num: number | null;
  text: string;
  type: "add" | "remove" | "context" | "empty";
};

export type SplitDiffRow = {
  left: SplitDiffCell;
  right: SplitDiffCell;
};

function linesFromChange(value: string) {
  return value.replace(/\n$/, "").split("\n").filter((line, index, lines) => line !== "" || index < lines.length - 1);
}

export function buildUnifiedDiffRows(oldSource: string, newSource: string): UnifiedDiffRow[] {
  let oldLine = 1;
  let newLine = 1;
  const rows: UnifiedDiffRow[] = [];

  for (const change of diffLines(oldSource, newSource)) {
    for (const line of linesFromChange(change.value)) {
      if (change.added) rows.push({ oldNum: null, newNum: newLine++, type: "add", text: line });
      else if (change.removed) rows.push({ oldNum: oldLine++, newNum: null, type: "remove", text: line });
      else rows.push({ oldNum: oldLine++, newNum: newLine++, type: "context", text: line });
    }
  }

  return rows;
}

export function buildSplitDiffRows(oldSource: string, newSource: string): SplitDiffRow[] {
  let oldLine = 1;
  let newLine = 1;
  const rows: SplitDiffRow[] = [];

  for (const change of diffLines(oldSource, newSource)) {
    const lines = linesFromChange(change.value);
    if (change.removed) {
      for (const line of lines) {
        rows.push({
          left: { num: oldLine++, text: line, type: "remove" },
          right: { num: null, text: "", type: "empty" },
        });
      }
    } else if (change.added) {
      for (let index = 0; index < lines.length; index += 1) {
        const candidate = rows[rows.length - lines.length + index];
        if (candidate?.right.type === "empty" && candidate.left.type === "remove") {
          candidate.right = { num: newLine++, text: lines[index], type: "add" };
        } else {
          rows.push({
            left: { num: null, text: "", type: "empty" },
            right: { num: newLine++, text: lines[index], type: "add" },
          });
        }
      }
    } else {
      for (const line of lines) {
        rows.push({
          left: { num: oldLine++, text: line, type: "context" },
          right: { num: newLine++, text: line, type: "context" },
        });
      }
    }
  }

  return rows;
}
