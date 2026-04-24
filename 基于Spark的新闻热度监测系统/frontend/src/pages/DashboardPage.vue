<template>
  <section class="page">
    <header class="page-header">
      <div>
        <div class="eyebrow">Dashboard</div>
        <h2>新闻监测可视化大屏</h2>
      </div>
      <div class="header-actions">
        <select v-model="scenario" class="field field--compact">
          <option value="general">常规场景</option>
          <option value="crisis">危机场景</option>
          <option value="policy">政策场景</option>
        </select>
        <button class="action-button" :disabled="running" @click="runPipeline">
          {{ running ? "正在抓取并分析..." : "抓取实时数据并分析" }}
        </button>
      </div>
    </header>

    <div v-if="pipelineSummary" class="status-banner">
      <div>
        <div class="status-banner__title">本次分析已完成</div>
        <div class="status-banner__text">
          共采集 {{ pipelineSummary.collected }} 条新闻，清洗后 {{ pipelineSummary.cleaned }} 条。
        </div>
      </div>
      <div class="status-grid">
        <span>RSS {{ pipelineSummary.rss_records }}</span>
        <span>网页 {{ pipelineSummary.web_records }}</span>
        <span>开放API {{ pipelineSummary.api_records }}</span>
        <span>样例 {{ pipelineSummary.sample_records }}</span>
        <span>引擎 {{ pipelineSummary.engine }}</span>
        <span>场景 {{ scenarioLabelMap[scenario] }}</span>
      </div>
    </div>

    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="stats-grid">
      <StatCard label="新闻总量" :value="overview.metrics.total_news" hint="当前已入库并完成分析的新闻数量" />
      <StatCard label="覆盖来源" :value="overview.metrics.total_sources" hint="当前参与统计的新闻来源数" />
      <StatCard label="事件簇数量" :value="overview.metrics.total_clusters" hint="自动聚类后的热点事件簇" />
      <StatCard label="平均热度" :value="overview.metrics.avg_hot_score" hint="根据来源、时效与情绪综合计算" />
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">来源分布</div>
        <div ref="sourceChartRef" class="chart"></div>
      </div>

      <div class="panel">
        <div class="panel__title">情感分布</div>
        <div ref="sentimentChartRef" class="chart"></div>
      </div>
    </div>

    <div class="panel-grid">
      <div class="panel panel--wide">
        <div class="panel__title">关键词趋势</div>
        <div ref="trendChartRef" class="chart chart--wide"></div>
      </div>
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">热点关键词</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>关键词</th>
              <th>热度</th>
              <th>新闻数</th>
            </tr>
          </thead>
          <tbody v-if="overview.hot_topics.length">
            <tr v-for="item in overview.hot_topics" :key="`${item.topic_label}-${item.bucket_time}`">
              <td>{{ item.topic_label }}</td>
              <td>{{ Number(item.score || 0).toFixed(2) }}</td>
              <td>{{ item.news_count }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="!overview.hot_topics.length" class="empty-state">当前没有热点数据，点击上方按钮抓取实时数据。</div>
      </div>

      <div class="panel">
        <div class="panel__title">预警列表</div>
        <ul v-if="overview.alerts.length" class="alert-list">
          <li v-for="item in overview.alerts" :key="`${item.alert_type}-${item.bucket_time}`">
            <span class="alert-list__level">{{ item.level }}</span>
            <span>{{ item.message }}</span>
          </li>
        </ul>
        <div v-else class="empty-state">当前没有触发预警，说明热点波动仍处于可控范围。</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import StatCard from "../components/StatCard.vue";
import { api } from "../services/api";

const scenarioLabelMap = {
  general: "常规",
  crisis: "危机",
  policy: "政策",
};

const scenario = ref("general");
const overview = ref({
  metrics: { total_news: 0, total_sources: 0, total_clusters: 0, avg_hot_score: 0 },
  source_distribution: [],
  sentiment_distribution: [],
  hot_topics: [],
  keyword_trends: [],
  alerts: [],
});

const pipelineSummary = ref(null);
const errorMessage = ref("");
const running = ref(false);
const sourceChartRef = ref(null);
const sentimentChartRef = ref(null);
const trendChartRef = ref(null);

let sourceChart;
let sentimentChart;
let trendChart;

function renderCharts() {
  if (sourceChartRef.value) {
    sourceChart ??= echarts.init(sourceChartRef.value);
    sourceChart.setOption({
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: ["42%", "72%"],
          data: overview.value.source_distribution,
          label: { color: "#d8e6f4" },
        },
      ],
    });
  }

  if (sentimentChartRef.value) {
    sentimentChart ??= echarts.init(sentimentChartRef.value);
    sentimentChart.setOption({
      color: ["#29c983", "#f2b134", "#ea5b5b"],
      tooltip: { trigger: "item" },
      series: [
        {
          type: "pie",
          radius: ["38%", "70%"],
          data: overview.value.sentiment_distribution,
          label: { color: "#d8e6f4" },
        },
      ],
    });
  }

  if (trendChartRef.value) {
    trendChart ??= echarts.init(trendChartRef.value);
    const items = overview.value.keyword_trends.slice(0, 12);
    trendChart.setOption({
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: items.map((item) => item.keyword),
        axisLabel: { color: "#d8e6f4", rotate: 20 },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#d8e6f4" },
      },
      series: [
        {
          type: "bar",
          data: items.map((item) => item.count),
          itemStyle: {
            color: "#ff8c42",
            borderRadius: [8, 8, 0, 0],
          },
        },
      ],
    });
  }
}

function resizeCharts() {
  sourceChart?.resize();
  sentimentChart?.resize();
  trendChart?.resize();
}

async function loadOverview() {
  try {
    const { data } = await api.getOverview();
    overview.value = data;
    await nextTick();
    renderCharts();
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "概览数据加载失败，请检查后端服务是否已启动。";
  }
}

async function runPipeline() {
  running.value = true;
  errorMessage.value = "";
  try {
    const { data } = await api.runPipeline({
      mode: "full",
      sample_limit: 0,
      rss_limit: 12,
      web_limit: 0,
      api_limit: 15,
      hot_score_scenario: scenario.value,
      include_sample: false,
      include_batch: false,
      include_rss: true,
      include_web: false,
      include_api: true,
      include_history: true,
      fast_live: false,
    });
    pipelineSummary.value = data.summary;
    await loadOverview();
  } catch (error) {
    errorMessage.value =
      error?.code === "ECONNABORTED"
        ? "实时抓取超时，后端仍可能在继续处理。请稍后刷新，或降低抓取范围后重试。"
        : error?.response?.data?.message || "实时抓取失败，请稍后重试。";
  } finally {
    running.value = false;
  }
}

onMounted(async () => {
  await loadOverview();
  window.addEventListener("resize", resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  sourceChart?.dispose();
  sentimentChart?.dispose();
  trendChart?.dispose();
});
</script>
