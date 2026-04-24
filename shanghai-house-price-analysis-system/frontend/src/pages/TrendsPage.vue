<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchDistrictStats, fetchPriceIndices } from '../api/client'
import ChartPanel from '../components/ChartPanel.vue'
import type { PriceIndex } from '../types'

const priceIndices = ref<PriceIndex[]>([])
const districtStats = ref<Array<{ district: string; listing_count: number; avg_unit_price: number; avg_total_price: number; avg_area: number }>>([])

const priceTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['环比指数', '同比指数'] },
  xAxis: { type: 'category', data: priceIndices.value.map((item) => item.stat_month) },
  yAxis: { type: 'value' },
  series: [
    { name: '环比指数', type: 'line', smooth: true, data: priceIndices.value.map((item) => item.mom_index), itemStyle: { color: '#722ed1' } },
    { name: '同比指数', type: 'line', smooth: true, data: priceIndices.value.map((item) => item.yoy_index), itemStyle: { color: '#f5222d' } },
  ],
}))

const districtAreaOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: districtStats.value.map((item) => item.district) },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      areaStyle: {},
      data: districtStats.value.map((item) => item.avg_area),
      itemStyle: { color: '#13c2c2' },
    },
  ],
}))

onMounted(async () => {
  priceIndices.value = await fetchPriceIndices()
  districtStats.value = await fetchDistrictStats()
})
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Trends</p>
        <h2>趋势分析</h2>
      </div>
      <p class="page-copy">结合国家统计局指数和样本区域指标，展示月度变化和区域结构。</p>
    </header>

    <div class="chart-grid">
      <ChartPanel title="官方二手住宅价格指数" :option="priceTrendOption" />
      <ChartPanel title="区域平均面积对比" :option="districtAreaOption" />
    </div>
  </section>
</template>
