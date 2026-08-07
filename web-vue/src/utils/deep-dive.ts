import { getFlowForVersion } from "@/data/execution-flows";
import type { FlowDefinition } from "@/data/execution-flows";

interface RawDecision {
  id: string;
  title: string;
  description: string;
  alternatives?: string;
  [locale: string]: unknown;
}

interface AnnotationFile {
  version: string;
  decisions: RawDecision[];
}

export interface DesignDecision {
  id: string;
  title: string;
  description: string;
  alternatives?: string;
}

const annotationModules = import.meta.glob("@/data/annotations/*.json", {
  eager: true,
  import: "default",
});

function annotationKey(version: string) {
  return `/src/data/annotations/${version}.json`;
}

export function getExecutionFlow(version: string): FlowDefinition {
  return getFlowForVersion(version) ?? { nodes: [], edges: [] };
}

export function getDesignDecisions(version: string, locale: string): DesignDecision[] {
  const annotation = annotationModules[annotationKey(version)] as AnnotationFile | undefined;
  if (!annotation) return [];

  return annotation.decisions.map((decision) => {
    const localized =
      locale !== "en" ? (decision[locale] as { title?: string; description?: string } | undefined) : undefined;

    return {
      id: decision.id,
      title: localized?.title || decision.title,
      description: localized?.description || decision.description,
      alternatives: decision.alternatives,
    };
  });
}
