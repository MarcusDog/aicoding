<template>
  <el-card v-if="detail.activity">
    <template #header>{{ detail.activity.title }}</template>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="类别">{{ detail.activity.categoryCode }}</el-descriptions-item>
      <el-descriptions-item label="地点">{{ detail.activity.location }}</el-descriptions-item>
      <el-descriptions-item label="开始时间">{{ detail.activity.startTime }}</el-descriptions-item>
      <el-descriptions-item label="结束时间">{{ detail.activity.endTime }}</el-descriptions-item>
      <el-descriptions-item label="服务时长">{{ detail.activity.serviceHours }} 小时</el-descriptions-item>
      <el-descriptions-item label="剩余名额">{{ detail.remainingCount }}</el-descriptions-item>
    </el-descriptions>
    <p style="margin-top:16px;line-height:1.8">{{ detail.activity.description }}</p>
    <div style="margin-top:16px">
      <el-tag v-if="detail.signup" type="success">当前报名状态：{{ detail.signup.signupStatus }}</el-tag>
      <el-button v-else type="primary" @click="handleApply">立即报名</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute } from 'vue-router';
import { applyActivity, getStudentActivityDetail } from '../../api/modules/student';

const route = useRoute();
const detail = reactive({});

const load = async () => {
  Object.assign(detail, await getStudentActivityDetail(route.params.id));
};

const handleApply = async () => {
  await applyActivity(route.params.id);
  ElMessage.success('报名成功');
  await load();
};

onMounted(load);
</script>
