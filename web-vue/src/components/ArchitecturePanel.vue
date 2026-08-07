<template>
  <section class="simple-panel architecture-panel">
    <h2>Architecture</h2>
    <div v-if="classes.length" class="class-stack">
      <article v-for="item in reversedClasses" :key="item.name" :class="{ fresh: newClassNames.has(item.name) }">
        <div>
          <strong>{{ item.name }}</strong>
          <span>introduced in {{ item.introducedIn }}</span>
        </div>
        <em v-if="newClassNames.has(item.name)">NEW</em>
      </article>
    </div>
    <p v-else>No classes in this version. The implementation is function based.</p>

    <div v-if="version?.tools.length" class="tool-cloud">
      <span v-for="tool in version.tools" :key="tool">{{ tool }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useAppStore } from "@/stores/app";
import { collectClassesForVersion, getNewClassNames } from "@/utils/learning";

const props = defineProps<{ versionId: string }>();
const app = useAppStore();

const data = computed(() => ({ versions: app.allVersions, diffs: app.allDiffs }));
const version = computed(() => app.getVersion(props.versionId));
const classes = computed(() => collectClassesForVersion(data.value, props.versionId));
const reversedClasses = computed(() => [...classes.value].reverse());
const newClassNames = computed(() => getNewClassNames(data.value, props.versionId));
</script>
