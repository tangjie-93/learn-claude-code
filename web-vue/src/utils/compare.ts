import type { AgentVersion, VersionIndex } from "@/types/agent-data";

function names<T extends { name: string }>(items: T[]) {
  return items.map((item) => item.name);
}

export interface VersionComparison {
  left: AgentVersion;
  right: AgentVersion;
  locDelta: number;
  toolsOnlyA: string[];
  toolsOnlyB: string[];
  toolsShared: string[];
  newClasses: string[];
  newFunctions: string[];
}

export function buildVersionComparison(
  data: VersionIndex,
  versionA: string,
  versionB: string,
): VersionComparison | null {
  const left = data.versions.find((version) => version.id === versionA);
  const right = data.versions.find((version) => version.id === versionB);
  if (!left || !right) return null;

  const leftTools = new Set(left.tools);
  const rightTools = new Set(right.tools);
  const leftClasses = new Set(names(left.classes));
  const leftFunctions = new Set(names(left.functions));

  return {
    left,
    right,
    locDelta: right.loc - left.loc,
    toolsOnlyA: left.tools.filter((tool) => !rightTools.has(tool)),
    toolsOnlyB: right.tools.filter((tool) => !leftTools.has(tool)),
    toolsShared: right.tools.filter((tool) => leftTools.has(tool)),
    newClasses: names(right.classes).filter((name) => !leftClasses.has(name)),
    newFunctions: names(right.functions).filter((name) => !leftFunctions.has(name)),
  };
}
