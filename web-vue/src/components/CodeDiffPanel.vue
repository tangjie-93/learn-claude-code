<template>
  <section class="simple-panel code-diff-panel">
    <div class="diff-toolbar">
      <span>{{ oldLabel }} -> {{ newLabel }}</span>
      <div>
        <button :class="{ active: mode === 'unified' }" type="button" @click="mode = 'unified'">Unified</button>
        <button :class="{ active: mode === 'split' }" type="button" @click="mode = 'split'">Split</button>
      </div>
    </div>

    <table v-if="mode === 'unified'" class="diff-table unified">
      <tbody>
        <tr v-for="(row, index) in unifiedRows" :key="index" :class="row.type">
          <td>{{ row.oldNum ?? "" }}</td>
          <td>{{ row.newNum ?? "" }}</td>
          <td>{{ row.type === "add" ? "+" : row.type === "remove" ? "-" : "" }}</td>
          <td>{{ row.text }}</td>
        </tr>
      </tbody>
    </table>

    <table v-else class="diff-table split">
      <tbody>
        <tr v-for="(row, index) in splitRows" :key="index">
          <td>{{ row.left.num ?? "" }}</td>
          <td :class="row.left.type">{{ row.left.text }}</td>
          <td>{{ row.right.num ?? "" }}</td>
          <td :class="row.right.type">{{ row.right.text }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { buildSplitDiffRows, buildUnifiedDiffRows } from "@/utils/code-diff";

const props = defineProps<{
  oldSource: string;
  newSource: string;
  oldLabel: string;
  newLabel: string;
}>();

const mode = ref<"unified" | "split">("unified");
const unifiedRows = computed(() => buildUnifiedDiffRows(props.oldSource, props.newSource));
const splitRows = computed(() => buildSplitDiffRows(props.oldSource, props.newSource));
</script>
