import { layers, versionMeta, versionOrder } from "@/data/constants";
import type { AgentVersion, VersionIndex } from "@/types/agent-data";

export function getLayerLegend() {
  return layers.map((layer) => ({
    id: layer.id,
    label: layer.label,
    versions: [...layer.versions],
  }));
}

export function getLocGrowthRows(versions: AgentVersion[]) {
  const versionMap = new Map(versions.map((version) => [version.id, version]));
  const maxLoc = Math.max(...versionOrder.map((id) => versionMap.get(id)?.loc ?? 0));

  return versionOrder.map((id) => {
    const version = versionMap.get(id);
    const loc = version?.loc ?? 0;
    return {
      id,
      loc,
      layer: versionMeta[id].layer,
      percent: Math.max(2, Math.round((loc / maxLoc) * 100)),
    };
  });
}

export function collectClassesForVersion(data: VersionIndex, targetId: string) {
  const targetIndex = data.versions.findIndex((version) => version.id === targetId);
  const target = targetIndex >= 0 ? data.versions[targetIndex] : undefined;

  return (
    target?.classes.map((cls) => ({
      name: cls.name,
      introducedIn:
        data.versions
          .slice(0, targetIndex + 1)
          .find((candidate) =>
            candidate.classes.some((candidateCls) => candidateCls.name === cls.name),
          )?.id ?? targetId,
    })) ?? []
  );
}

export function getNewClassNames(data: VersionIndex, version: string) {
  const diff = data.diffs.find((item) => item.to === version);
  if (diff) return new Set(diff.newClasses);

  const target = data.versions.find((item) => item.id === version);
  return new Set(target?.classes.map((item) => item.name) ?? []);
}

export function getVersionDiffSummary(data: VersionIndex, version: string) {
  return data.diffs.find((item) => item.to === version) ?? null;
}
