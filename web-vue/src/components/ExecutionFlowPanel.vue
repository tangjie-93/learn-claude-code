<template>
  <section class="simple-panel execution-flow-panel">
    <h2>Execution flow</h2>
    <svg v-if="flow.nodes.length" class="flow-svg" :viewBox="viewBox" role="img">
      <defs>
        <marker id="flow-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 8 4 L 0 8 z" />
        </marker>
      </defs>
      <path
        v-for="edge in drawableEdges"
        :key="`${edge.from}-${edge.to}-${edge.label || ''}`"
        class="flow-edge"
        :d="edge.path"
        marker-end="url(#flow-arrow)"
      />
      <g v-for="node in flow.nodes" :key="node.id" :class="['flow-shape', `node-${node.type}`]">
        <polygon
          v-if="node.type === 'decision'"
          :points="diamondPoints(node)"
        />
        <rect
          v-else
          :x="node.x - metrics(node).width / 2"
          :y="node.y - metrics(node).height / 2"
          :width="metrics(node).width"
          :height="metrics(node).height"
          :rx="node.type === 'start' || node.type === 'end' ? metrics(node).height / 2 : 8"
        />
        <text
          v-for="(line, index) in metrics(node).lines"
          :key="`${node.id}-${index}`"
          :x="node.x"
          :y="node.y + (index - (metrics(node).lines.length - 1) / 2) * 13"
          text-anchor="middle"
          dominant-baseline="central"
        >
          {{ line }}
        </text>
      </g>
    </svg>
    <p v-if="!flow.nodes.length">No execution flow data for this version.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getExecutionFlow } from "@/utils/deep-dive";
import { getEdgePath, getFlowViewBox, getNodeMetrics } from "@/utils/flow-layout";
import type { FlowNode } from "@/types/agent-data";

const props = defineProps<{ versionId: string }>();
const flow = computed(() => getExecutionFlow(props.versionId));
const viewBox = computed(() => getFlowViewBox(flow.value.nodes));
const nodeMap = computed(() => new Map(flow.value.nodes.map((node) => [node.id, node])));
const drawableEdges = computed(() =>
  flow.value.edges.flatMap((edge) => {
    const from = nodeMap.value.get(edge.from);
    const to = nodeMap.value.get(edge.to);
    return from && to ? [{ ...edge, path: getEdgePath(from, to) }] : [];
  }),
);

function metrics(node: FlowNode) {
  return getNodeMetrics(node);
}

function diamondPoints(node: FlowNode) {
  const nodeMetrics = getNodeMetrics(node);
  const halfW = nodeMetrics.width / 2;
  const halfH = nodeMetrics.height / 2;
  return `${node.x},${node.y - halfH} ${node.x + halfW},${node.y} ${node.x},${node.y + halfH} ${node.x - halfW},${node.y}`;
}
</script>
