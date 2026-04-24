<template>
  <el-row :gutter="16">
    <el-col :span="24">
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>活动统计报表</span>
            <el-button type="primary" plain @click="downloadActivityReport">导出活动报表</el-button>
          </div>
        </template>
        <el-table :data="activityRows" border>
          <el-table-column label="活动名称" min-width="220">
            <template #default="{ row }">{{ row.activity?.title || '-' }}</template>
          </el-table-column>
          <el-table-column prop="signupCount" label="报名人数" width="100" />
          <el-table-column prop="approvedCount" label="通过人数" width="100" />
          <el-table-column prop="signCount" label="签到人数" width="100" />
          <el-table-column prop="completedCount" label="完成人数" width="100" />
          <el-table-column prop="totalHours" label="累计时长" width="120" />
        </el-table>
      </el-card>
    </el-col>

    <el-col :span="12" style="margin-top: 16px;">
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>学生时长统计</span>
            <el-button type="primary" plain @click="downloadStudentHoursReport">导出学生报表</el-button>
          </div>
        </template>
        <el-table :data="studentRows" border>
          <el-table-column label="姓名" min-width="100">
            <template #default="{ row }">{{ row.student?.name || '-' }}</template>
          </el-table-column>
          <el-table-column label="学院" min-width="160">
            <template #default="{ row }">{{ row.student?.collegeName || '-' }}</template>
          </el-table-column>
          <el-table-column label="累计时长" width="120">
            <template #default="{ row }">{{ row.student?.totalServiceHours || 0 }}</template>
          </el-table-column>
          <el-table-column prop="confirmedCount" label="已完成活动数" width="130" />
        </el-table>
      </el-card>
    </el-col>

    <el-col :span="12" style="margin-top: 16px;">
      <el-card>
        <template #header>月度趋势统计</template>
        <ChartPanel :option="monthlyActivityOption" />
        <div style="height: 16px;"></div>
        <ChartPanel :option="monthlyHoursOption" />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';
import {
  exportActivityReport,
  exportStudentHoursReport,
  getActivityReport,
  getMonthlyReport,
  getStudentHoursReport
} from '../../api/modules/admin';
import ChartPanel from '../../components/ChartPanel.vue';

const activityRows = ref([]);
const studentRows = ref([]);
const monthly = ref({});

const monthlyKeys = computed(() => {
  const keys = new Set([
    ...Object.keys(monthly.value.activityCount || {}),
    ...Object.keys(monthly.value.totalHours || {})
  ]);
  return [...keys].sort();
});

const monthlyActivityOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: monthlyKeys.value
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      name: '活动数',
      type: 'line',
      smooth: true,
      data: monthlyKeys.value.map((key) => monthly.value.activityCount?.[key] || 0),
      itemStyle: { color: '#2563eb' }
    }
  ]
}));

const monthlyHoursOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: monthlyKeys.value
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '累计时长',
      type: 'bar',
      data: monthlyKeys.value.map((key) => Number(monthly.value.totalHours?.[key] || 0)),
      itemStyle: { color: '#f97316' }
    }
  ]
}));

const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
};

const downloadActivityReport = async () => {
  const response = await exportActivityReport();
  downloadBlob(response.data, 'activity-report.csv');
  ElMessage.success('活动报表已下载');
};

const downloadStudentHoursReport = async () => {
  const response = await exportStudentHoursReport();
  downloadBlob(response.data, 'student-hours-report.csv');
  ElMessage.success('学生报表已下载');
};

onMounted(async () => {
  activityRows.value = (await getActivityReport()).records || [];
  studentRows.value = (await getStudentHoursReport()).records || [];
  monthly.value = await getMonthlyReport();
});
</script>
