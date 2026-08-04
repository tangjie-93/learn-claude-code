<template>
  <section class="source-panel">
    <div class="source-header">
      <span>{{ filename }}</span>
      <span>{{ lineCount }} lines</span>
    </div>
    <pre><code>{{ source }}</code></pre>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ filename: string; source: string }>();
const lineCount = computed(() => props.source.split("\n").length);
</script>
