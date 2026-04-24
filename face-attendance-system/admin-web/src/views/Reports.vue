<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>统计报表</span>
        <div class="toolbar">
          <el-date-picker v-model="month" type="month" value-format="YYYY-MM" placeholder="选择月份" />
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="exportCsv">导出 CSV</el-button>
        </div>
      </div>
    </template>

    <el-table :data="items" border v-loading="loading">
      <el-table-column prop="user_id" label="用户ID" width="90" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="department" label="部门" />
      <el-table-column prop="total" label="签到次数" />
      <el-table-column prop="normal" label="正常" />
      <el-table-column prop="late" label="迟到" />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

import { getMonthlyReport } from "../api/admin";

const month = ref("");
const items = ref([]);
const loading = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getMonthlyReport({ month: month.value || undefined });
    items.value = result.data.items || [];
  } catch (error) {
    ElMessage.error(error.message || "加载报表失败");
  } finally {
    loading.value = false;
  }
};

const exportCsv = async () => {
  try {
    const base = import.meta.env.VITE_API_BASE || "http://localhost:5000/api";
    const token = localStorage.getItem("attendance_admin_token");
    const url = `${base}/admin/export${month.value ? `?month=${month.value}` : ""}`;
    const response = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) throw new Error(`导出失败: HTTP ${response.status}`);
    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "attendance-report.csv";
    link.click();
    URL.revokeObjectURL(link.href);
    ElMessage.success("导出成功");
  } catch (error) {
    ElMessage.error(error.message || "导出失败");
  }
};

loadData();
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  gap: 10px;
}
</style>
