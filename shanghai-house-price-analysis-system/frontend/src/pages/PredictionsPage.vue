<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchPredictions } from '../api/client'
import ChartPanel from '../components/ChartPanel.vue'
import type { Prediction } from '../types'

const predictions = ref<Prediction[]>([])

const predictionOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: predictions.value.map((item) => item.target_name) },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      data: predictions.value.map((item) => item.predicted_unit_price),
      itemStyle: { color: '#fa8c16' },
    },
  ],
}))

onMounted(async () => {
  predictions.value = await fetchPredictions()
})
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Prediction</p>
        <h2>预测结果</h2>
      </div>
      <p class="page-copy">展示区域级预测单价和置信区间，可作为论文中模型结果页截图。</p>
    </header>

    <div class="chart-grid single">
      <ChartPanel title="区域预测单价" :option="predictionOption" />
    </div>

    <div class="table-shell">
      <table class="data-table">
        <thead>
          <tr>
            <th>目标层级</th>
            <th>目标名称</th>
            <th>模型</th>
            <th>预测单价</th>
            <th>下界</th>
            <th>上界</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in predictions" :key="item.id">
            <td>{{ item.target_level }}</td>
            <td>{{ item.target_name }}</td>
            <td>{{ item.model_name }}</td>
            <td>{{ item.predicted_unit_price }}</td>
            <td>{{ item.confidence_lower }}</td>
            <td>{{ item.confidence_upper }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
