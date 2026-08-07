<template>
  <div class="home-view home-stack">
    <section class="hero">
      <h1>{{ app.t("home", "hero_title") }}</h1>
      <p>{{ app.t("home", "hero_subtitle") }}</p>
      <RouterLink class="primary-action" :to="`/${app.locale}/timeline`">
        {{ app.t("home", "start") }}
        <span aria-hidden="true">-&gt;</span>
      </RouterLink>
    </section>

    <section class="home-section">
      <div class="home-section-heading">
        <h2>{{ app.t("home", "core_pattern") }}</h2>
        <p>{{ app.t("home", "core_pattern_desc") }}</p>
      </div>
      <div class="core-code-card">
        <div class="core-code-titlebar">
          <span />
          <span />
          <span />
          <strong>agent_loop.py</strong>
        </div>
        <pre><code><span class="code-purple">while</span> <span class="code-orange">True</span><span class="code-muted">:</span>
    response = client.messages.<span class="code-blue">create</span><span class="code-muted">(</span>messages=messages, tools=tools<span class="code-muted">)</span>
    <span class="code-purple">if</span> response.stop_reason != <span class="code-green">"tool_use"</span><span class="code-muted">:</span>
        <span class="code-purple">break</span>
    <span class="code-purple">for</span> tool_call <span class="code-purple">in</span> response.content<span class="code-muted">:</span>
        result = <span class="code-blue">execute_tool</span><span class="code-muted">(</span>tool_call.name, tool_call.input<span class="code-muted">)</span>
        messages.<span class="code-blue">append</span><span class="code-muted">(</span>result<span class="code-muted">)</span></code></pre>
      </div>
    </section>

    <section class="home-section">
      <div class="home-section-heading">
        <h2>{{ app.t("home", "message_flow") }}</h2>
        <p>{{ app.t("home", "message_flow_desc") }}</p>
      </div>
      <div class="message-flow-wrap">
        <MessageFlow />
      </div>
    </section>

    <section class="section">
      <div class="home-section-heading">
        <h2>{{ app.t("home", "learning_path") }}</h2>
        <p>{{ app.t("home", "learning_path_desc") }}</p>
      </div>
      <div class="version-grid">
        <RouterLink
          v-for="id in app.versionOrder"
          :key="id"
          class="version-card"
          :to="`/${app.locale}/${id}`"
        >
          <div class="card-topline">
            <LayerBadge :layer="app.versionMeta[id].layer">{{ id }}</LayerBadge>
            <span>{{ app.getVersion(id)?.loc ?? 0 }} {{ app.t("home", "loc") }}</span>
          </div>
          <h3>{{ app.versionLabel(id) }}</h3>
          <p>{{ app.versionMeta[id].keyInsight }}</p>
        </RouterLink>
      </div>
    </section>

    <section class="section">
      <div class="home-section-heading">
        <h2>{{ app.t("home", "layers_title") }}</h2>
        <p>{{ app.t("home", "layers_desc") }}</p>
      </div>
      <div class="layer-list">
        <article v-for="layer in app.layers" :key="layer.id" class="layer-row">
          <div :class="['layer-stripe', `layer-${layer.id}`]" />
          <div>
            <div class="layer-row-title">
              <h3>{{ app.t("layer_labels", layer.id) }}</h3>
              <span>{{ layer.versions.length }} {{ app.t("home", "versions_in_layer") }}</span>
            </div>
            <div class="badge-row">
              <RouterLink v-for="version in layer.versions" :key="version" :to="`/${app.locale}/${version}`">
                <LayerBadge :layer="layer.id">{{ version }}: {{ app.versionLabel(version) }}</LayerBadge>
              </RouterLink>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeMount } from "vue";
import { RouterLink, useRoute } from "vue-router";
import LayerBadge from "@/components/LayerBadge.vue";
import MessageFlow from "@/components/MessageFlow.vue";
import { useAppStore } from "@/stores/app";

const app = useAppStore();
const route = useRoute();

onBeforeMount(() => app.setLocale(String(route.params.locale || "en")));
</script>
