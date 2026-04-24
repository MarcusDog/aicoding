<template>
  <el-card>
    <template #header>时长认定</template>
    <el-table :data="rows" border>
      <el-table-column prop="activity.title" label="活动" />
      <el-table-column prop="student.name" label="学生" />
      <el-table-column prop="record.hoursValue" label="时长" />
      <el-table-column prop="record.hoursStatus" label="状态" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button link type="success" @click="confirm(row.record.id)">确认</el-button>
          <el-button link type="danger" @click="revoke(row.record.id)">撤销</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { confirmHours, getHours, revokeHours } from '../../api/modules/admin';

const rows = ref([]);

const load = async () => {
  rows.value = await getHours();
};

const confirm = async (id) => {
  await confirmHours(id, { remark: '管理员确认' });
  ElMessage.success('确认成功');
  await load();
};

const revoke = async (id) => {
  await revokeHours(id, { remark: '管理员撤销' });
  ElMessage.success('撤销成功');
  await load();
};

onMounted(load);
</script>
