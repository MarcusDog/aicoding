<template>
  <el-card>
    <template #header>我的报名</template>
    <el-table :data="rows" border>
      <el-table-column prop="activity.title" label="活动名称" />
      <el-table-column prop="activity.location" label="地点" />
      <el-table-column prop="signup.signupStatus" label="报名状态" />
      <el-table-column prop="sign.signStatus" label="签到状态" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button
            v-if="['PENDING','APPROVED'].includes(row.signup.signupStatus)"
            type="danger"
            link
            @click="handleCancel(row.signup.id)"
          >
            取消报名
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { cancelSignup, getMySignups } from '../../api/modules/student';

const rows = ref([]);

const load = async () => {
  rows.value = await getMySignups();
};

const handleCancel = async (id) => {
  await ElMessageBox.confirm('确认取消报名吗？', '提示');
  await cancelSignup(id, { cancelReason: '学生主动取消' });
  ElMessage.success('取消成功');
  await load();
};

onMounted(load);
</script>
