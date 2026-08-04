export type AgentLayer =
  | "tools"
  | "planning"
  | "memory"
  | "concurrency"
  | "collaboration";

export interface ChapterImage {
  src: string;
  alt: string;
}

export interface AgentVersion {
  id: string;
  filename: string;
  title: string;
  subtitle: string;
  loc: number;
  tools: string[];
  newTools: string[];
  coreAddition: string;
  keyInsight: string;
  classes: { name: string; startLine: number; endLine: number }[];
  functions: { name: string; signature: string; startLine: number }[];
  layer: AgentLayer;
  source: string;
  images: ChapterImage[];
}

export interface VersionDiff {
  from: string;
  to: string;
  newClasses: string[];
  newFunctions: string[];
  newTools: string[];
  locDelta: number;
}

export interface DocContent {
  version: string;
  locale: "en" | "zh" | "ja";
  title: string;
  content: string;
}

export interface VersionIndex {
  versions: AgentVersion[];
  diffs: VersionDiff[];
}

export interface ScenarioStep {
  type: string;
  content: string;
  annotation?: string;
  toolName?: string;
  toolInput?: string;
}

export interface Scenario {
  version: string;
  title: string;
  description: string;
  steps: ScenarioStep[];
}

export interface FlowNode {
  id: string;
  label: string;
  type: "start" | "process" | "decision" | "subprocess" | "end";
  x: number;
  y: number;
}

export interface FlowEdge {
  from: string;
  to: string;
  label?: string;
}
