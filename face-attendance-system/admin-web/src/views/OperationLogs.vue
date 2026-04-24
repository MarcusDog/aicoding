<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>操作日志</span>
        <div class="filters">
          <el-select v-model="query.operator_type" clearable placeholder="操作者类型" style="width: 130px">
            <el-option label="管理员" value="admin" />
            <el-option label="用户" value="user" />
          </el-select>
          <el-input v-model="query.action" clearable placeholder="动作名" style="width: 180px" />
          <el-button type="primary" @click="fetchLogs">查询</el-button>
        </div>
      </div>
    </template>

    <el-table :data="items" border v-loading="loading">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="operator_type" label="类型" width="100" />
      <el-table-column prop="operator_id" label="操作者ID" width="110" />
      <el-table-column prop="action" label="动作" width="160" />
      <el-table-column prop="detail" label="详情" min-width="260" />
      <el-table-column prop="ip_address" label="IP" width="140" />
      <el-table-column prop="created_at" label="时间" width="200" />
    </el-table>

    <el-pagination
      style="margin-top: 16px"
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.size"
      :current-page="query.page"
      @current-change="handlePageChange"
    />
  </el-card>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { getLogs } from "../api/admin";

const loading = ref(false);
const items = ref([]);
const total = ref(0);
const query = reactive({
  page: 1,
  size: 10,
  action: "",
  operator_type: "",
});

const fetchLogs = async () => {
  loading.value = true;
  try {
    const result = await getLogs(query);
    items.value = result.data.items || [];
    total.value = result.data.total || 0;
  } catch (error) {
    ElMessage.error(error.message || "加载日志失败");
  } finally {
    loading.value = false;
  }
};

const handlePageChange = async (page) => {
  query.page = page;
  await fetchLogs();
};

fetchLogs();
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 10px;
}
</style>
