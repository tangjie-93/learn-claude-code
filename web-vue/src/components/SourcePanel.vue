<template>
  <section class="source-panel">
    <div class="source-header">
      <div class="source-window-dots" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <span>{{ filename }}</span>
    </div>
    <div class="source-scroll">
      <pre><code><div v-for="(line, index) in lines" :key="index" class="source-line"><span>{{ index + 1 }}</span><span :class="lineClass(line)">{{ line }}</span></div></code></pre>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ filename: string; source: string }>();
const lines = computed(() => props.source.split("\n"));

function lineClass(line: string) {
  const trimmed = line.trimStart();
  return {
    "source-comment": trimmed.startsWith("#"),
    "source-decorator": trimmed.startsWith("@"),
    "source-docstring": trimmed.startsWith('"""') || trimmed.startsWith("'''"),
  };
}
</script>
