<template>
  <section class="page">
    <header class="page-header">
      <div>
        <div class="eyebrow">Services</div>
        <h2>服务中心与来源管理</h2>
      </div>
    </header>

    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="stats-grid">
      <StatCard label="总来源数" :value="catalog.total_sources || 0" hint="目录中登记的数据来源总数" />
      <StatCard label="可采集来源" :value="catalog.collectable_sources || 0" hint="当前系统可直接采集的真实来源" />
      <StatCard label="预警快报" :value="alertBriefs.length" hint="已生成的预警摘要条数" />
      <StatCard label="服务角色" :value="Object.keys(serviceBriefs).length" hint="已开放的角色化数据服务类型" />
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel__title">来源目录</div>
        <div class="source-list">
          <article v-for="item in catalog.items.slice(0, 48)" :key="`${item.catalog_section}-${item.name}`" class="source-card">
            <div class="cluster-card__meta">
              <span>{{ item.catalog_section }}</span>
              <span>优先级 {{ item.priority || 0 }}</span>
            </div>
            <h3>{{ item.name }}</h3>
            <p>{{ item.organization }}</p>
            <div class="cluster-card__tags">
              <span>{{ item.adapter }}</span>
              <span>{{ item.category }}</span>
              <span>{{ item.region }}</span>
              <span>{{ item.enabled ? "enabled" : "planned" }}</span>
            </div>
          </article>
        </div>
      </div>

      <div class="panel">
        <div class="panel__title">预警快报</div>
        <div v-if="alertBriefs.length" class="cluster-list">
          <article v-for="item in alertBriefs" :key="`${item.alert_type}-${item.bucket_time}`" class="cluster-card">
            <div class="cluster-card__meta">
              <span>{{ item.level }}</span>
              <span>{{ formatTime(item.bucket_time) }}</span>
            </div>
            <h3>{{ item.message }}</h3>
            <p>{{ item.应对建议 }}</p>
            <div class="cluster-card__tags">
              <span v-for="source in item.sources" :key="source">{{ source }}</span>
            </div>
          </article>
        </div>
        <div v-else class="empty-state">当前尚未生成预警快报。</div>
      </div>
    </div>

    <div class="panel-grid">
      <div class="panel" v-for="(brief, role) in serviceBriefs" :key="role">
        <div class="panel__title">{{ roleLabelMap[role] || role }}</div>
        <div class="service-brief">
          <template v-for="(value, key) in brief" :key="`${role}-${key}`">
            <div class="service-brief__item">
              <strong>{{ key }}</strong>
              <div v-if="Array.isArray(value)" class="cluster-card__tags">
                <span v-for="entry in normalizeArray(value)" :key="entry">{{ entry }}</span>
              </div>
              <div v-else-if="typeof value === 'object'">
                <pre class="service-brief__json">{{ JSON.stringify(value, null, 2) }}</pre>
              </div>
              <div v-else class="table-subtext">{{ value }}</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import StatCard from "../components/StatCard.vue";
import { api } from "../services/api";

const roleLabelMap = {
  media: "媒体服务",
  pr: "公关服务",
  government: "政务服务",
  research: "研究服务",
};

const catalog = ref({ total_sources: 0, collectable_sources: 0, items: [] });
const alertBriefs = ref([]);
const serviceBriefs = ref({});
const errorMessage = ref("");

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN");
}

function normalizeArray(value) {
  return value.map((item) => (typeof item === "string" ? item : JSON.stringify(item, null, 0)));
}

async function loadData() {
  errorMessage.value = "";
  try {
    const [catalogResponse, alertResponse, briefResponse] = await Promise.all([
      api.getSourceCatalog(),
      api.getAlertBriefs(),
      api.getServiceBriefs(),
    ]);
    catalog.value = catalogResponse.data;
    alertBriefs.value = alertResponse.data;
    serviceBriefs.value = briefResponse.data;
  } catch (error) {
    errorMessage.value = error?.response?.data?.message || "服务中心数据加载失败。";
  }
}

onMounted(loadData);
</script>
