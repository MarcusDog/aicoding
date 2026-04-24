<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>人脸库管理</span>
        <div class="filters">
          <el-input
            v-model="query.keyword"
            placeholder="姓名/工号"
            clearable
            style="width: 220px"
            @keyup.enter="fetchFaces"
          />
          <el-button type="primary" @click="fetchFaces">查询</el-button>
        </div>
      </div>
    </template>

    <el-table :data="items" border v-loading="loading">
      <el-table-column prop="id" label="用户ID" width="90" />
      <el-table-column prop="name" label="姓名" width="140" />
      <el-table-column prop="employee_no" label="工号" width="140" />
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column label="注册状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_face_registered ? 'success' : 'warning'">
            {{ row.is_face_registered ? "已注册" : "未注册" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="质量分" width="100">
        <template #default="{ row }">
          {{ row.face_data?.quality_score ?? "-" }}
        </template>
      </el-table-column>
      <el-table-column label="人脸图片路径" min-width="240">
        <template #default="{ row }">
          <el-tooltip :content="row.face_data?.face_image_path || '-'" placement="top-start">
            <span class="truncate">{{ row.face_data?.face_image_path || "-" }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="180">
        <template #default="{ row }">{{ row.face_data?.updated_at || row.updated_at || "-" }}</template>
      </el-table-column>
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

import { getFaces } from "../api/admin";

const loading = ref(false);
const items = ref([]);
const total = ref(0);

const query = reactive({
  page: 1,
  size: 10,
  keyword: "",
});

const fetchFaces = async () => {
  loading.value = true;
  try {
    const result = await getFaces(query);
    items.value = result.data.items || [];
    total.value = result.data.total || 0;
  } catch (error) {
    ElMessage.error(error.message || "加载人脸数据失败");
  } finally {
    loading.value = false;
  }
};

const handlePageChange = async (page) => {
  query.page = page;
  await fetchFaces();
};

fetchFaces();
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

.truncate {
  display: inline-block;
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
