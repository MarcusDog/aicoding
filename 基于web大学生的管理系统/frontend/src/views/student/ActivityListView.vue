<template>
  <el-card>
    <template #header>
      <div style="display:flex;gap:12px">
        <el-input v-model="keyword" placeholder="按活动名称搜索" style="max-width:260px" />
        <el-select v-model="status" placeholder="状态筛选" clearable style="width:180px">
          <el-option label="已发布" value="PUBLISHED" />
          <el-option label="报名截止" value="SIGNUP_CLOSED" />
          <el-option label="进行中" value="IN_PROGRESS" />
          <el-option label="已完成" value="COMPLETED" />
        </el-select>
        <el-button type="primary" @click="load">查询</el-button>
      </div>
    </template>
    <el-table :data="activities" border>
      <el-table-column prop="title" label="活动名称" />
      <el-table-column prop="categoryCode" label="类别" />
      <el-table-column prop="location" label="地点" />
      <el-table-column prop="startTime" label="开始时间" />
      <el-table-column prop="serviceHours" label="时长" />
      <el-table-column prop="activityStatus" label="状态" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getStudentActivities } from '../../api/modules/student';

const router = useRouter();
const activities = ref([]);
const keyword = ref('');
const status = ref('');

const load = async () => {
  activities.value = await getStudentActivities({ keyword: keyword.value, status: status.value });
};

const goDetail = (id) => router.push(`/student/activities/${id}`);

onMounted(load);
</script>
