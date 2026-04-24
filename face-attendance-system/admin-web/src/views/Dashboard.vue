<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6"><el-card><div class="title">员工总数</div><div class="num">{{ data.today.total_users }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="title">今日签到</div><div class="num">{{ data.today.present_users }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="title">迟到人数</div><div class="num">{{ data.today.late_count }}</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="title">签到率</div><div class="num">{{ data.today.check_in_rate }}%</div></el-card></el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <el-card>
          <template #header>近7日签到趋势</template>
          <div ref="trendRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>待处理事项</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="未注册人脸">{{ data.pending.unregistered_faces }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import * as echarts from "echarts";
import { nextTick, onMounted, reactive, ref } from "vue";

import { getDashboard } from "../api/admin";

const trendRef = ref(null);
const data = reactive({
  today: { total_users: 0, present_users: 0, late_count: 0, check_in_rate: 0 },
  trend: [],
  pending: { unregistered_faces: 0 },
});

const renderChart = () => {
  if (!trendRef.value) return;
  const chart = echarts.init(trendRef.value);
  chart.setOption({
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.trend.map((item) => item.date) },
    yAxis: { type: "value" },
    series: [{ type: "line", smooth: true, data: data.trend.map((item) => item.count), areaStyle: {} }],
  });
};

onMounted(async () => {
  const result = await getDashboard();
  Object.assign(data, result.data);
  await nextTick();
  renderChart();
});
</script>

<style scoped>
.title {
  color: #64748b;
}

.num {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}

.chart {
  height: 320px;
}
</style>
