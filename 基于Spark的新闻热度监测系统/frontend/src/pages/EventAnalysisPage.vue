<template>
  <section class="page">
    <header class="page-header">
      <div>
        <div class="eyebrow">Events</div>
        <h2>事件聚类与关联分析</h2>
      </div>
    </header>

    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">情感统计</div>
        <div ref="sentimentChartRef" class="chart"></div>
      </div>

      <div class="panel">
        <div class="panel__title">事件簇列表</div>
        <div v-if="clusters.length" class="cluster-list">
          <article
            v-for="item in clusters"
            :key="item.cluster_key"
            class="cluster-card"
            :class="{ 'cluster-card--active': selectedClusterKey === item.cluster_key }"
            @click="selectCluster(item.cluster_key)"
          >
            <div class="cluster-card__meta">
              <span>{{ sentimentLabelMap[item.sentiment_summary] || item.sentiment_summary }}</span>
              <span>{{ item.news_count }} 篇</span>
            </div>
            <h3>{{ item.label }}</h3>
            <p>{{ item.representative_title }}</p>
            <div class="cluster-card__tags">
              <span v-for="keyword in item.keywords" :key="keyword">{{ keyword }}</span>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">当前没有事件聚类结果，请先在大屏页抓取实时数据。</div>
      </div>
    </div>

    <div v-if="selectedDetail" class="panel-grid">
      <div class="panel panel--wide">
        <div class="panel__title">事件全景</div>
        <div class="event-overview">
          <div class="event-overview__main">
            <h3>{{ selectedDetail.representative_title }}</h3>
            <p>聚类标签：{{ selectedDetail.label }}</p>
            <p>事件评分：{{ Number(selectedDetail.score || 0).toFixed(2) }}</p>
          </div>
          <div class="event-overview__facts">
            <div><strong>Who：</strong>{{ formatWho(selectedDetail.fivew1h?.who) }}</div>
            <div><strong>When：</strong>{{ formatWhen(selectedDetail.fivew1h?.when) }}</div>
            <div><strong>Where：</strong>{{ selectedDetail.fivew1h?.where || "全网" }}</div>
            <div><strong>What：</strong>{{ selectedDetail.fivew1h?.what || "-" }}</div>
            <div><strong>Why：</strong>{{ selectedDetail.fivew1h?.why || "-" }}</div>
            <div><strong>How：</strong>{{ selectedDetail.fivew1h?.how || "-" }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedDetail" class="panel-grid">
      <div class="panel">
        <div class="panel__title">传播路径</div>
        <ul class="timeline-list">
          <li v-for="item in selectedDetail.spread_path" :key="`${item.source}-${item.publish_time}`">
            <span class="timeline-list__time">{{ formatTime(item.publish_time) }}</span>
            <div>
              <div>{{ item.source }}</div>
              <div class="table-subtext">{{ item.title }}</div>
            </div>
          </li>
        </ul>
      </div>

      <div class="panel">
        <div class="panel__title">媒体倾向</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>媒体</th>
              <th>篇数</th>
              <th>倾向</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in selectedDetail.media_tendency" :key="item.source">
              <td>{{ item.source }}</td>
              <td>{{ item.count }}</td>
              <td>{{ item.tendency }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedDetail" class="panel panel--wide">
      <div class="panel__title">事件时间线</div>
      <ul class="timeline-list">
        <li v-for="item in selectedDetail.timeline" :key="item.news_id">
          <span class="timeline-list__time">{{ formatTime(item.publish_time) }}</span>
          <div>
            <a class="table-link" :href="item.url" target="_blank">{{ item.title }}</a>
            <div class="table-subtext">{{ item.source }} · {{ item.sentiment_display }}</div>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import { api } from "../services/api";

const sentimentLabelMap = {
  positive: "正面",
  neutral: "中性",
  negative: "负面",
};

const clusters = ref([]);
const sentimentRows = ref([]);
const selectedClusterKey = ref("");
const selectedDetail = ref(null);
const sentimentChartRef = ref(null);
const errorMessage = ref("");

let chart;

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN");
}

function formatWhen(range) {
  if (!range?.start && !range?.end) return "-";
  return `${formatTime(range?.start)} 至 ${formatTime(range?.end)}`;
}

function formatWho(items) {
  if (!items?.length) return "-";
  return items.map(([name, count]) => `${name}(${count})`).join("、");
}

function renderChart() {
  if (!sentimentChartRef.value) return;
  chart ??= echarts.init(sentimentChartRef.value);
  chart.setOption({
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: sentimentRows.value.map((item) => sentimentLabelMap[item.label] || item.label),
      axisLabel: { color: "#d8e6f4" },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#d8e6f4" },
    },
    series: [
      {
        type: "bar",
        data: sentimentRows.value.map((item) => item.count),
        itemStyle: {
          color: "#29c983",
          borderRadius: [8, 8, 0, 0],
        },
      },
    ],
  });
}

function resizeChart() {
  chart?.resize();
}

async function loadDetail(clusterKey) {
  if (!clusterKey) return;
  const { data } = await api.getEventDetail({ cluster_key: clusterKey });
  selectedDetail.value = data;
  selectedClusterKey.value = clusterKey;
}

async function loadData() {
  errorMessage.value = "";
  try {
    const [eventResponse, sentimentResponse] = await Promise.all([
      api.getEvents({ limit: 12 }),
      api.getSentimentSummary(),
    ]);
    clusters.value = eventResponse.data;
    sentimentRows.value = sentimentResponse.data;
    await nextTick();
    renderChart();
    if (clusters.value.length) {
      await loadDetail(clusters.value[0].cluster_key);
    }
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "事件分析数据加载失败。";
  }
}

async function selectCluster(clusterKey) {
  try {
    await loadDetail(clusterKey);
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "事件详情加载失败。";
  }
}

onMounted(async () => {
  await loadData();
  window.addEventListener("resize", resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeChart);
  chart?.dispose();
});
</script>
