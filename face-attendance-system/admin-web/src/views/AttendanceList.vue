<template>
  <el-card>
    <template #header>考勤记录</template>
    <div class="filters">
      <el-input v-model="query.user_id" placeholder="用户ID" style="width: 160px" />
      <el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" placeholder="日期" />
      <el-button @click="fetchList">筛选</el-button>
    </div>

    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="user_id" label="用户ID" width="90" />
      <el-table-column prop="user_name" label="姓名" width="120" />
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column prop="rule_id" label="规则ID" width="90" />
      <el-table-column prop="check_time" label="签到时间" />
      <el-table-column prop="status" label="状态" width="90" />
      <el-table-column prop="face_match_score" label="匹配分" width="100" />
      <el-table-column prop="device_info" label="设备信息" />
    </el-table>

    <el-pagination
      style="margin-top: 16px"
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.size"
      :current-page="query.page"
      @current-change="(page) => { query.page = page; fetchList(); }"
    />
  </el-card>
</template>

<script setup>
import { reactive, ref } from "vue";

import { getAttendance } from "../api/admin";

const items = ref([]);
const total = ref(0);

const query = reactive({
  page: 1,
  size: 10,
  user_id: "",
  date: "",
});

const fetchList = async () => {
  const params = { ...query };
  if (!params.user_id) delete params.user_id;
  if (!params.date) delete params.date;
  const result = await getAttendance(params);
  items.value = result.data.items;
  total.value = result.data.total;
};

fetchList();
</script>

<style scoped>
.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
</style>
