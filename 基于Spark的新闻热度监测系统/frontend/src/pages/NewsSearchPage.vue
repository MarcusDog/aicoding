<template>
  <section class="page">
    <header class="page-header">
      <div>
        <div class="eyebrow">Search</div>
        <h2>新闻查询与导出</h2>
      </div>
      <a class="action-button" href="/api/export/news?format=csv" target="_blank">导出全部 CSV</a>
    </header>

    <div class="filter-bar">
      <input v-model="filters.q" class="field" placeholder="输入关键词" @keyup.enter="submitSearch" />
      <select v-model="filters.source" class="field">
        <option value="">全部来源</option>
        <option v-for="source in sources" :key="source" :value="source">{{ source }}</option>
      </select>
      <select v-model="filters.category" class="field">
        <option value="">全部类别</option>
        <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
      </select>
      <select v-model="filters.sentiment" class="field">
        <option value="">全部情感</option>
        <option value="positive">正面</option>
        <option value="neutral">中性</option>
        <option value="negative">负面</option>
      </select>
      <input v-model="filters.date_from" class="field" type="date" />
      <input v-model="filters.date_to" class="field" type="date" />
      <input v-model="filters.hot_min" class="field" type="number" step="0.1" placeholder="最低热度" />
      <button class="action-button" :disabled="loading" @click="submitSearch">
        {{ loading ? "查询中..." : "查询" }}
      </button>
      <a class="action-button" :href="exportHref" target="_blank">导出当前结果</a>
    </div>

    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="panel">
      <div class="panel__title">查询结果</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>标题</th>
            <th>来源</th>
            <th>发布时间</th>
            <th>情感</th>
            <th>热度</th>
          </tr>
        </thead>
        <tbody v-if="items.length">
          <tr v-for="item in items" :key="item.news_id">
            <td>
              <a class="table-link" :href="item.url" target="_blank">{{ item.title }}</a>
              <div class="table-subtext">{{ item.summary }}</div>
            </td>
            <td>{{ item.source }}</td>
            <td>{{ formatTime(item.publish_time) }}</td>
            <td>{{ sentimentLabelMap[item.sentiment_label] || "未知" }}</td>
            <td>{{ Number(item.hot_score || 0).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="!items.length" class="empty-state">暂无符合条件的数据，请先到大屏页执行实时抓取。</div>

      <div class="pager">
        <span>共 {{ pagination.total }} 条</span>
        <button class="page-button" :disabled="pagination.page <= 1 || loading" @click="changePage(-1)">上一页</button>
        <span>第 {{ pagination.page }} 页</span>
        <button
          class="page-button"
          :disabled="pagination.page * pagination.page_size >= pagination.total || loading"
          @click="changePage(1)"
        >
          下一页
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "../services/api";

const sentimentLabelMap = {
  positive: "正面",
  neutral: "中性",
  negative: "负面",
};

const filters = ref({
  q: "",
  source: "",
  category: "",
  sentiment: "",
  date_from: "",
  date_to: "",
  hot_min: "",
  page: 1,
  page_size: 10,
});

const items = ref([]);
const sources = ref([]);
const categories = ref([]);
const pagination = ref({ page: 1, page_size: 10, total: 0 });
const loading = ref(false);
const errorMessage = ref("");

const exportHref = computed(() => {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters.value)) {
    if (value !== "" && key !== "page" && key !== "page_size") {
      params.set(key, value);
    }
  }
  params.set("format", "csv");
  return `/api/export/news?${params.toString()}`;
});

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN");
}

async function loadNews() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const { data } = await api.getNews(filters.value);
    items.value = data.items;
    sources.value = data.sources;
    categories.value = data.categories || [];
    pagination.value = data.pagination;
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "新闻查询失败，请确认后端接口可访问。";
  } finally {
    loading.value = false;
  }
}

function submitSearch() {
  filters.value.page = 1;
  loadNews();
}

function changePage(offset) {
  filters.value.page += offset;
  loadNews();
}

onMounted(loadNews);
</script>
