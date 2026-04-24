<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchOverview } from '../api/client'
import ChartPanel from '../components/ChartPanel.vue'
import MetricCard from '../components/MetricCard.vue'
import type { OverviewPayload } from '../types'

const overview = ref<OverviewPayload | null>(null)

const districtOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: overview.value?.charts.district_distribution.map((item) => item.district) ?? [] },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      data: overview.value?.charts.district_distribution.map((item) => item.avg_unit_price) ?? [],
      itemStyle: { color: '#165dff' },
    },
  ],
}))

const predictionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: overview.value?.charts.latest_predictions.map((item) => item.target_name) ?? [] },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      smooth: true,
      data: overview.value?.charts.latest_predictions.map((item) => item.predicted_unit_price) ?? [],
      itemStyle: { color: '#ff7d00' },
    },
  ],
}))

onMounted(async () => {
  overview.value = await fetchOverview()
})
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Dashboard</p>
        <h2>市场总览</h2>
      </div>
      <p class="page-copy">展示当前房源量、均价、价格区间和区域分布，用于答辩首页说明。</p>
    </header>

    <div v-if="overview" class="metric-grid">
      <MetricCard label="房源数量" :value="String(overview.metrics.listing_count)" hint="当前已导入的可分析房源数" />
      <MetricCard label="小区数量" :value="String(overview.metrics.community_count)" hint="当前可用于小区维度分析的样本数" />
      <MetricCard label="平均单价" :value="`${overview.metrics.avg_unit_price.toLocaleString()} 元/平`" hint="样本房源平均挂牌单价" />
      <MetricCard label="平均总价" :value="`${overview.metrics.avg_total_price.toLocaleString()} 万`" hint="样本房源平均挂牌总价" />
    </div>

    <div v-if="overview" class="chart-grid">
      <ChartPanel title="区域均价对比" :option="districtOption" />
      <ChartPanel title="预测结果快照" :option="predictionOption" />
    </div>
  </section>
</template>
