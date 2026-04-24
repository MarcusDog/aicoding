<template>
  <div ref="chartRef" style="height: 320px; width: 100%;"></div>
</template>

<script setup>
import * as echarts from 'echarts';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = defineProps({
  option: {
    type: Object,
    required: true
  }
});

const chartRef = ref(null);
let chartInstance;

const renderChart = () => {
  if (!chartRef.value) {
    return;
  }
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  chartInstance.setOption(props.option, true);
};

onMounted(() => {
  renderChart();
  window.addEventListener('resize', renderChart);
});

watch(() => props.option, () => {
  renderChart();
}, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderChart);
  if (chartInstance) {
    chartInstance.dispose();
  }
});
</script>
