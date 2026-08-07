<template>
  <div class="architecture-panel">
    <div v-if="classes.length" class="class-stack">
      <template v-for="(item, index) in reversedClasses" :key="item.name">
        <article
          :class="[
            { fresh: newClassNames.has(item.name) },
            newClassNames.has(item.name) ? `fresh-${app.versionMeta[item.introducedIn]?.layer || 'default'}` : '',
          ]"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <span>{{ classDescriptions[item.name] || `Introduced in ${item.introducedIn}` }}</span>
          </div>
          <em v-if="newClassNames.has(item.name)">NEW</em>
        </article>
        <div v-if="index < reversedClasses.length - 1" class="class-arrow" aria-hidden="true">↓</div>
      </template>
    </div>
    <p v-else>No classes in this version. The implementation is function based.</p>

    <div v-if="version?.tools.length" class="tool-cloud">
      <span v-for="tool in version.tools" :key="tool">{{ tool }}</span>
    </div>
  </div>
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

const classDescriptions: Record<string, string> = {
  Agent: "Main orchestration loop",
  Session: "Conversation state + persistence",
  ToolRegistry: "Tool discovery and dispatch",
  ContextManager: "Context window management",
  MemoryManager: "Long-term memory retrieval",
  CronScheduler: "Background scheduled runs",
  MultiAgentCoordinator: "Parallel sub-agent coordination",
  TodoManager: "Visible task planning with constraints",
  SkillLoader: "Dynamic knowledge injection from SKILL.md files",
  Task: "File-based persistent task with dependencies",
  TaskManager: "File-based persistent task CRUD with dependencies",
  BackgroundTask: "Single background execution unit",
  BackgroundManager: "Non-blocking thread execution + notification queue",
  TeammateManager: "Multi-agent team lifecycle and coordination",
  Teammate: "Individual agent identity and state tracking",
  SharedBoard: "Cross-agent shared state coordination",
  ProtocolState: "Pending team protocol requests and response matching",
  MCPClient: "External tool discovery and invocation client",
  RecoveryState: "Retry, fallback, and continuation state",
};
</script>
