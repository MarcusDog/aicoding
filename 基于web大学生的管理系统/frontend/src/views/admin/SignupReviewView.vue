<template>
  <el-card>
    <template #header>报名审核</template>
    <el-table :data="rows" border>
      <el-table-column prop="activity.title" label="活动" />
      <el-table-column prop="student.name" label="学生" />
      <el-table-column prop="signup.signupStatus" label="状态" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button v-if="row.signup.signupStatus === 'PENDING'" link type="success" @click="approve(row.signup.id)">通过</el-button>
          <el-button v-if="row.signup.signupStatus === 'PENDING'" link type="danger" @click="reject(row.signup.id)">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { approveSignup, getSignups, rejectSignup } from '../../api/modules/admin';

const rows = ref([]);

const load = async () => {
  rows.value = await getSignups();
};

const approve = async (id) => {
  await approveSignup(id, { reviewComment: '审核通过' });
  ElMessage.success('已通过');
  await load();
};

const reject = async (id) => {
  await rejectSignup(id, { reviewComment: '审核驳回' });
  ElMessage.success('已驳回');
  await load();
};

onMounted(load);
</script>
