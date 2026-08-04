<template>
  <article class="markdown-body" v-html="html" />
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ content: string }>();

function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function inlineMarkdown(value: string) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}

const html = computed(() => {
  const lines = props.content.split("\n");
  const output: string[] = [];
  let inCode = false;
  let inList = false;

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.startsWith("```")) {
      if (inCode) {
        output.push("</code></pre>");
        inCode = false;
      } else {
        output.push("<pre><code>");
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      output.push(`${escapeHtml(raw)}\n`);
      continue;
    }
    if (/^-\s+/.test(line)) {
      if (!inList) {
        output.push("<ul>");
        inList = true;
      }
      output.push(`<li>${inlineMarkdown(line.replace(/^-\s+/, ""))}</li>`);
      continue;
    }
    if (inList) {
      output.push("</ul>");
      inList = false;
    }
    if (line.startsWith("# ")) output.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`);
    else if (line.startsWith("## ")) output.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
    else if (line.startsWith("### ")) output.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
    else if (line.startsWith("![")) {
      const match = line.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
      if (match) output.push(`<img src="${match[2]}" alt="${escapeHtml(match[1])}" />`);
    } else if (line.trim()) output.push(`<p>${inlineMarkdown(line)}</p>`);
  }

  if (inList) output.push("</ul>");
  if (inCode) output.push("</code></pre>");
  return output.join("\n");
});
</script>
