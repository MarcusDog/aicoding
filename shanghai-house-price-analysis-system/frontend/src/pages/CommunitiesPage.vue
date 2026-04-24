<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchCommunities } from '../api/client'
import ChartPanel from '../components/ChartPanel.vue'
import type { Community } from '../types'

const communities = ref<Community[]>([])

const topCommunities = computed(() =>
  [...communities.value]
    .sort((left, right) => right.averageUnitPrice - left.averageUnitPrice)
    .slice(0, 8),
)

const communityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: topCommunities.value.map((item) => item.name) },
  series: [
    {
      type: 'bar',
      data: topCommunities.value.map((item) => item.averageUnitPrice),
      itemStyle: { color: '#36cfc9' },
    },
  ],
}))

onMounted(async () => {
  communities.value = await fetchCommunities()
})
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Communities</p>
        <h2>小区分析</h2>
      </div>
      <p class="page-copy">从小区维度对均价、建成年份和在售套数进行展示。</p>
    </header>

    <div class="chart-grid single">
      <ChartPanel title="小区均价 Top 8" :option="communityOption" />
    </div>

    <div class="table-shell">
      <table class="data-table">
        <thead>
          <tr>
            <th>小区</th>
            <th>区域</th>
            <th>板块</th>
            <th>均价</th>
            <th>建成年份</th>
            <th>在售套数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in communities" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.district }}</td>
            <td>{{ item.subdistrict }}</td>
            <td>{{ item.averageUnitPrice }}</td>
            <td>{{ item.buildYear }}</td>
            <td>{{ item.onSaleCount }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
