<template>
  <section class="page">
    <header class="page-header">
      <div>
        <div class="eyebrow">Influence</div>
        <h2>传播影响力与互动热度看板</h2>
      </div>
      <div class="header-actions">
        <button class="action-button" @click="loadData">刷新传播分析</button>
      </div>
    </header>

    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="stats-grid">
      <StatCard label="真实互动总量" :value="viewModel.metrics.total_interactions || 0" hint="优先汇总真实点赞、评论、热度分值和社区投票数据" />
      <StatCard label="有互动新闻" :value="viewModel.metrics.articles_with_real_interactions || 0" hint="至少包含一项真实互动字段的新闻条目数" />
      <StatCard label="高热平台" :value="viewModel.metrics.top_platform || '-'" hint="按互动总量排名的头部平台" />
      <StatCard label="高热区域" :value="viewModel.metrics.top_region || '-'" hint="按互动与新闻量综合排名的区域" />
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">平台热度看板</div>
        <div ref="platformChartRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel__title">区域热度看板</div>
        <div ref="regionChartRef" class="chart"></div>
      </div>
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">来源影响力排行</div>
        <div ref="sourceChartRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel__title">传播路径网络</div>
        <div ref="networkChartRef" class="chart"></div>
      </div>
    </div>

    <div class="panel panel--wide">
      <div class="panel__title">事件传播评估</div>
      <div v-if="viewModel.event_influence.length" class="event-metrics-grid">
        <article v-for="item in viewModel.event_influence" :key="item.cluster_key" class="event-metric-card">
          <div class="cluster-card__meta">
            <span>{{ item.lifecycle_stage }}</span>
            <span>种子源 {{ item.seed_source }}</span>
          </div>
          <h3>{{ item.label || item.representative_title }}</h3>
          <p>{{ item.representative_title }}</p>
          <div class="cluster-card__tags">
            <span>互动 {{ item.interaction_total }}</span>
            <span>来源覆盖 {{ item.source_coverage }}</span>
            <span>平台覆盖 {{ item.platform_coverage }}</span>
            <span>扩散速率 {{ Number(item.spread_speed || 0).toFixed(2) }}/h</span>
            <span>平均热度 {{ Number(item.avg_hot_score || 0).toFixed(2) }}</span>
          </div>
        </article>
      </div>
      <div v-else class="empty-state">当前没有可展示的传播事件，请先完成一次采集和分析。</div>
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">平台明细</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>平台</th>
              <th>新闻数</th>
              <th>互动总量</th>
              <th>平均热度</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in viewModel.platform_heat" :key="item.platform">
              <td>{{ item.platform }}</td>
              <td>{{ item.news_count }}</td>
              <td>{{ item.interaction_total }}</td>
              <td>{{ Number(item.avg_hot_score || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="panel">
        <div class="panel__title">区域明细</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>区域</th>
              <th>新闻数</th>
              <th>互动总量</th>
              <th>平均热度</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in viewModel.region_heat" :key="item.region">
              <td>{{ item.region }}</td>
              <td>{{ item.news_count }}</td>
              <td>{{ item.interaction_total }}</td>
              <td>{{ Number(item.avg_hot_score || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import StatCard from "../components/StatCard.vue";
import { api } from "../services/api";

const defaultOverview = {
  metrics: {
    total_interactions: 0,
    articles_with_real_interactions: 0,
    top_platform: "-",
    top_region: "-",
  },
  region_heat: [],
  platform_heat: [],
  source_influence: [],
  event_influence: [],
  network: { nodes: [], links: [] },
};
const overview = ref({ ...defaultOverview });
const viewModel = computed(() => ({
  ...defaultOverview,
  ...(overview.value || {}),
  metrics: {
    ...defaultOverview.metrics,
    ...((overview.value && overview.value.metrics) || {}),
  },
  region_heat: Array.isArray(overview.value?.region_heat) ? overview.value.region_heat : [],
  platform_heat: Array.isArray(overview.value?.platform_heat) ? overview.value.platform_heat : [],
  source_influence: Array.isArray(overview.value?.source_influence) ? overview.value.source_influence : [],
  event_influence: Array.isArray(overview.value?.event_influence) ? overview.value.event_influence : [],
  network: {
    nodes: Array.isArray(overview.value?.network?.nodes) ? overview.value.network.nodes : [],
    links: Array.isArray(overview.value?.network?.links) ? overview.value.network.links : [],
  },
}));
const errorMessage = ref("");

const platformChartRef = ref(null);
const regionChartRef = ref(null);
const sourceChartRef = ref(null);
const networkChartRef = ref(null);

let platformChart;
let regionChart;
let sourceChart;
let networkChart;

function renderCharts() {
  if (platformChartRef.value) {
    platformChart ??= echarts.init(platformChartRef.value);
    platformChart.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: 50, right: 16, top: 24, bottom: 44 },
      xAxis: {
        type: "category",
        data: viewModel.value.platform_heat.map((item) => item.platform),
        axisLabel: { color: "#d8e6f4", rotate: 18 },
      },
      yAxis: { type: "value", axisLabel: { color: "#d8e6f4" } },
      series: [
        {
          type: "bar",
          data: viewModel.value.platform_heat.map((item) => item.interaction_total),
          itemStyle: { color: "#ff8c42", borderRadius: [10, 10, 0, 0] },
        },
      ],
    });
  }

  if (regionChartRef.value) {
    regionChart ??= echarts.init(regionChartRef.value);
    regionChart.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: 60, right: 24, top: 24, bottom: 24 },
      xAxis: { type: "value", axisLabel: { color: "#d8e6f4" } },
      yAxis: {
        type: "category",
        data: viewModel.value.region_heat.map((item) => item.region),
        axisLabel: { color: "#d8e6f4" },
      },
      series: [
        {
          type: "bar",
          data: viewModel.value.region_heat.map((item) => item.interaction_total),
          itemStyle: { color: "#29c983", borderRadius: [0, 10, 10, 0] },
        },
      ],
    });
  }

  if (sourceChartRef.value) {
    sourceChart ??= echarts.init(sourceChartRef.value);
    sourceChart.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: 60, right: 18, top: 24, bottom: 44 },
      xAxis: {
        type: "category",
        data: viewModel.value.source_influence.map((item) => item.source),
        axisLabel: { color: "#d8e6f4", rotate: 24 },
      },
      yAxis: { type: "value", axisLabel: { color: "#d8e6f4" } },
      series: [
        {
          type: "line",
          smooth: true,
          data: viewModel.value.source_influence.map((item) => item.interaction_total),
          lineStyle: { color: "#6dd5ff", width: 3 },
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(109, 213, 255, 0.42)" },
                { offset: 1, color: "rgba(109, 213, 255, 0.02)" },
              ],
            },
          },
        },
      ],
    });
  }

  if (networkChartRef.value) {
    networkChart ??= echarts.init(networkChartRef.value);
    networkChart.setOption({
      tooltip: {},
      series: [
        {
          type: "graph",
          layout: "force",
          roam: true,
          draggable: true,
          force: { repulsion: 220, edgeLength: [60, 120] },
          data: viewModel.value.network.nodes.map((node) => ({
            ...node,
            symbolSize: Math.max(18, Math.min(48, Math.sqrt(node.value || 1) * 2.2)),
            itemStyle: { color: node.platform?.includes("News") ? "#ff8c42" : "#29c983" },
            label: { show: true, color: "#f5f7fa" },
          })),
          links: viewModel.value.network.links.map((link) => ({
            ...link,
            lineStyle: { width: Math.max(1, link.value || 1), color: "rgba(216, 230, 244, 0.35)" },
          })),
        },
      ],
    });
  }
}

function resizeCharts() {
  platformChart?.resize();
  regionChart?.resize();
  sourceChart?.resize();
  networkChart?.resize();
}

async function loadData() {
  errorMessage.value = "";
  try {
    const { data } = await api.getInfluenceOverview();
    overview.value = data || { ...defaultOverview };
    await nextTick();
    renderCharts();
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "传播影响力数据加载失败。";
  }
}

onMounted(async () => {
  await loadData();
  window.addEventListener("resize", resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  platformChart?.dispose();
  regionChart?.dispose();
  sourceChart?.dispose();
  networkChart?.dispose();
});
</script>
