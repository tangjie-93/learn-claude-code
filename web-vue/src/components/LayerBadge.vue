<template>
  <span :class="['layer-badge', `layer-${layer}`]">
    <slot />
  </span>
</template>

<script setup lang="ts">
import type { AgentLayer } from "@/types/agent-data";

defineProps<{ layer: AgentLayer }>();
</script>
