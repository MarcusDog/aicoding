<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  title: string
  option: Record<string, unknown>
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value) {
    return
  }
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption(props.option as echarts.EChartsOption, true)
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', renderChart)
})

watch(
  () => props.option,
  () => {
    renderChart()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderChart)
  chart?.dispose()
})
</script>

<template>
  <section class="panel">
    <header class="panel-header">
      <h3>{{ title }}</h3>
    </header>
    <div ref="chartRef" class="chart-box" />
  </section>
</template>
