<template>
  <div>
    <div class="card-grid">
      <el-card>
        <div>活动总数</div>
        <h2>{{ summary.activityCount || 0 }}</h2>
      </el-card>
      <el-card>
        <div>报名总数</div>
        <h2>{{ summary.signupCount || 0 }}</h2>
      </el-card>
      <el-card>
        <div>已完成活动</div>
        <h2>{{ summary.completedActivityCount || 0 }}</h2>
      </el-card>
      <el-card>
        <div>累计服务时长</div>
        <h2>{{ summary.totalServiceHours || 0 }}</h2>
      </el-card>
    </div>

    <div class="chart-grid">
      <el-card>
        <template #header>按月份统计活动数</template>
        <ChartPanel :option="monthOption" />
      </el-card>
      <el-card>
        <template #header>按类别统计活动数</template>
        <ChartPanel :option="categoryOption" />
      </el-card>
      <el-card>
        <template #header>各学院累计服务时长</template>
        <ChartPanel :option="collegeHoursOption" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue';
import { getDashboard } from '../../api/modules/admin';
import ChartPanel from '../../components/ChartPanel.vue';

const dashboard = reactive({});
const summary = computed(() => dashboard.summary || {});

const monthEntries = computed(() => Object.entries(dashboard.activityByMonth || {}));
const categoryEntries = computed(() => Object.entries(dashboard.activityByCategory || {}));
const collegeEntries = computed(() => Object.entries(dashboard.hoursByCollege || {}));

const monthOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: monthEntries.value.map(([key]) => key)
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      name: '活动数',
      type: 'bar',
      data: monthEntries.value.map(([, value]) => value),
      itemStyle: { color: '#2563eb' }
    }
  ]
}));

const categoryOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [
    {
      name: '活动类别',
      type: 'pie',
      radius: ['35%', '65%'],
      data: categoryEntries.value.map(([name, value]) => ({ name, value }))
    }
  ]
}));

const collegeHoursOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    axisLabel: { interval: 0, rotate: 18 },
    data: collegeEntries.value.map(([key]) => key)
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '累计时长',
      type: 'bar',
      data: collegeEntries.value.map(([, value]) => Number(value)),
      itemStyle: { color: '#0f766e' }
    }
  ]
}));

onMounted(async () => {
  Object.assign(dashboard, await getDashboard());
});
</script>
