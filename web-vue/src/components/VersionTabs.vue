<template>
  <div class="tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="{ active: active === tab.id }"
      type="button"
      @click="active = tab.id"
    >
      {{ tab.label }}
    </button>
  </div>
  <slot :active="active" />
</template>

<script setup lang="ts">
import { ref } from "vue";

defineProps<{ tabs: { id: string; label: string }[] }>();
const active = ref("learn");
</script>
