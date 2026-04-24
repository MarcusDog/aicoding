<template>
  <el-card>
    <template #header>我的时长</template>
    <el-table :data="records" border>
      <el-table-column prop="activityId" label="活动ID" />
      <el-table-column prop="hoursValue" label="时长" />
      <el-table-column prop="hoursStatus" label="状态" />
      <el-table-column prop="generatedAt" label="生成时间" />
      <el-table-column prop="remark" label="备注" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { getMyHours } from '../../api/modules/student';

const records = ref([]);

onMounted(async () => {
  records.value = await getMyHours();
});
</script>
