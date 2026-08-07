import type { FlowNode } from "@/types/agent-data";

const nodeWidth = 140;
const nodeHeight = 44;
const diamondWidth = 92;
const diamondHeight = 64;
const loopRailX = -48;
const rightLoopRailX = 576;
const flowCenterX = 300;
const loopPad = 28;
const loopBackDxLimit = 360;
const loopBackDyLimit = 70;

export interface NodeMetrics {
  lines: string[];
  width: number;
  height: number;
}

export function getNodeLines(node: FlowNode) {
  const maxChars = node.type === "decision" ? 12 : 18;
  return node.label.split("\n").flatMap((line) => {
    if (line.length <= maxChars) return [line];
    const parts = line.split(/(\s+\/\s+|\s+|_)/).filter(Boolean);
    const chunks: string[] = [];
    let current = "";
    for (const part of parts) {
      const next = `${current}${part}`;
      if (current && next.trim().length > maxChars) {
        chunks.push(current.trim());
        current = part.trimStart();
      } else {
        current = next;
      }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks.length ? chunks : [line];
  });
}

function estimateTextWidth(line: string, fontSize: number) {
  return line.length * fontSize * 0.62;
}

export function getNodeMetrics(node: FlowNode): NodeMetrics {
  const lines = getNodeLines(node);
  const longest = Math.max(...lines.map((line) => estimateTextWidth(line, 11)), 0);
  if (node.type === "decision") {
    return {
      lines,
      width: Math.max(diamondWidth, longest + 54),
      height: Math.max(diamondHeight, lines.length * 15 + 42),
    };
  }
  if (node.type === "start" || node.type === "end") {
    return {
      lines,
      width: Math.max(nodeWidth, longest + 34),
      height: Math.max(nodeHeight, lines.length * 15 + 24),
    };
  }
  return {
    lines,
    width: Math.max(nodeWidth, longest + 30),
    height: Math.max(nodeHeight, lines.length * 15 + 24),
  };
}

export function getNodeBounds(node: FlowNode) {
  const metrics = getNodeMetrics(node);
  const halfW = metrics.width / 2;
  const halfH = metrics.height / 2;
  return {
    cx: node.x,
    cy: node.y,
    left: node.x - halfW,
    right: node.x + halfW,
    top: node.y - halfH,
    bottom: node.y + halfH,
  };
}

function getLoopSide(start: ReturnType<typeof getNodeBounds>, end: ReturnType<typeof getNodeBounds>) {
  return (start.cx + end.cx) / 2 > flowCenterX ? "right" : "left";
}

function getLoopRailX(
  start: ReturnType<typeof getNodeBounds>,
  end: ReturnType<typeof getNodeBounds>,
  side = getLoopSide(start, end),
) {
  if (side === "right") {
    return Math.max(rightLoopRailX, start.right + loopPad, end.right + loopPad);
  }
  return Math.min(loopRailX, start.left - loopPad, end.left - loopPad);
}

function isLoopBack(start: ReturnType<typeof getNodeBounds>, end: ReturnType<typeof getNodeBounds>) {
  const dx = end.cx - start.cx;
  const dy = end.cy - start.cy;
  return dy < -loopBackDyLimit && Math.abs(dx) <= loopBackDxLimit;
}

function shouldUseStepRoute(start: ReturnType<typeof getNodeBounds>, end: ReturnType<typeof getNodeBounds>) {
  const dx = end.cx - start.cx;
  const dy = end.cy - start.cy;
  return dy > 28 && Math.abs(dx) > 44 && end.top > start.bottom;
}

function getStepBusY(start: ReturnType<typeof getNodeBounds>, end: ReturnType<typeof getNodeBounds>) {
  const room = end.top - start.bottom;
  return Math.min(end.top - 16, start.bottom + Math.max(18, room * 0.35));
}

export function getEdgePath(from: FlowNode, to: FlowNode) {
  const start = getNodeBounds(from);
  const end = getNodeBounds(to);
  const dx = end.cx - start.cx;
  const dy = end.cy - start.cy;

  if (isLoopBack(start, end)) {
    const side = getLoopSide(start, end);
    const railX = getLoopRailX(start, end, side);
    const startX = side === "right" ? start.right : start.left;
    const endX = side === "right" ? end.right : end.left;
    const midY = (start.cy + end.cy) / 2;
    return `M ${startX} ${start.cy} C ${railX} ${start.cy}, ${railX} ${midY}, ${railX} ${midY} C ${railX} ${end.cy}, ${endX} ${end.cy}, ${endX} ${end.cy}`;
  }

  if (Math.abs(dx) < 10) {
    return dy >= 0
      ? `M ${start.cx} ${start.bottom} L ${end.cx} ${end.top}`
      : `M ${start.cx} ${start.top} L ${end.cx} ${end.bottom}`;
  }

  if (Math.abs(dy) < 10) {
    const startX = dx > 0 ? start.right : start.left;
    const endX = dx > 0 ? end.left : end.right;
    const midX = (startX + endX) / 2;
    return `M ${startX} ${start.cy} C ${midX} ${start.cy}, ${midX} ${end.cy}, ${endX} ${end.cy}`;
  }

  if (shouldUseStepRoute(start, end)) {
    const busY = getStepBusY(start, end);
    return `M ${start.cx} ${start.bottom} L ${start.cx} ${busY} L ${end.cx} ${busY} L ${end.cx} ${end.top}`;
  }

  const startX = dx > 0 ? start.right : start.left;
  const endX = dx > 0 ? end.left : end.right;
  const control = Math.max(56, Math.abs(dx) * 0.45);
  return `M ${startX} ${start.cy} C ${startX + (dx > 0 ? control : -control)} ${start.cy}, ${endX - (dx > 0 ? control : -control)} ${end.cy}, ${endX} ${end.cy}`;
}

export function getFlowViewBox(nodes: FlowNode[]) {
  if (!nodes.length) return "0 0 640 420";
  const bounds = nodes.map(getNodeBounds);
  const left = Math.min(...bounds.map((item) => item.left), loopRailX) - 24;
  const top = Math.min(...bounds.map((item) => item.top)) - 24;
  const right = Math.max(...bounds.map((item) => item.right), rightLoopRailX) + 24;
  const bottom = Math.max(...bounds.map((item) => item.bottom)) + 32;
  return `${left} ${top} ${right - left} ${bottom - top}`;
}
