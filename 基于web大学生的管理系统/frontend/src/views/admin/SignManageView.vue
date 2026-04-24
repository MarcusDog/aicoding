<template>
  <el-card>
    <template #header>签到管理</template>
    <el-table :data="rows" border>
      <el-table-column label="活动" min-width="220">
        <template #default="{ row }">{{ row.activity?.title || '-' }}</template>
      </el-table-column>
      <el-table-column label="学生" width="110">
        <template #default="{ row }">{{ row.student?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="签到状态" width="120">
        <template #default="{ row }">{{ row.sign?.signStatus || '-' }}</template>
      </el-table-column>
      <el-table-column label="签到时间" min-width="180">
        <template #default="{ row }">{{ row.sign?.signInTime || '-' }}</template>
      </el-table-column>
      <el-table-column label="签退时间" min-width="180">
        <template #default="{ row }">{{ row.sign?.signOutTime || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openFixDialog(row)">补录</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="补录签到" width="600px">
    <el-form :model="fixForm" label-width="100px">
      <el-form-item label="签到时间">
        <el-date-picker
          v-model="fixForm.signInTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item label="签退时间">
        <el-date-picker
          v-model="fixForm.signOutTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item label="异常说明">
        <el-input v-model="fixForm.exceptionRemark" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submitFix">确认补录</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { fixSign, getSigns } from '../../api/modules/admin';

const rows = ref([]);
const visible = ref(false);
const editingId = ref(null);
const fixForm = reactive({
  signInTime: '',
  signOutTime: '',
  exceptionRemark: '管理员补录签到'
});

const load = async () => {
  rows.value = await getSigns();
};

const openFixDialog = (row) => {
  editingId.value = row.sign?.id;
  Object.assign(fixForm, {
    signInTime: row.sign?.signInTime || row.activity?.startTime || '',
    signOutTime: row.sign?.signOutTime || row.activity?.endTime || '',
    exceptionRemark: row.sign?.exceptionRemark || '管理员补录签到'
  });
  visible.value = true;
};

const submitFix = async () => {
  await fixSign(editingId.value, {
    signInTime: fixForm.signInTime,
    signOutTime: fixForm.signOutTime,
    exceptionRemark: fixForm.exceptionRemark
  });
  ElMessage.success('补录成功');
  visible.value = false;
  await load();
};

onMounted(load);
</script>
