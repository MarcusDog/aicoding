<template>
  <el-card>
    <template #header>个人中心</template>
    <el-form :model="profile" label-width="90px" style="max-width:680px">
      <el-form-item label="学号"><el-input v-model="profile.studentNo" disabled /></el-form-item>
      <el-form-item label="姓名"><el-input v-model="profile.name" disabled /></el-form-item>
      <el-form-item label="学院"><el-input v-model="profile.collegeName" disabled /></el-form-item>
      <el-form-item label="专业"><el-input v-model="profile.majorName" disabled /></el-form-item>
      <el-form-item label="班级"><el-input v-model="profile.className" disabled /></el-form-item>
      <el-form-item label="电话"><el-input v-model="profile.phone" /></el-form-item>
      <el-form-item label="邮箱"><el-input v-model="profile.email" /></el-form-item>
      <el-form-item label="头像">
        <UploadField v-model="profile.avatarUrl" upload-path="/files/upload/avatar" button-text="上传头像" />
      </el-form-item>
      <el-form-item label="备注"><el-input v-model="profile.remark" type="textarea" /></el-form-item>
      <el-button type="primary" @click="save">保存修改</el-button>
    </el-form>
  </el-card>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { getMyProfile, updateMyProfile } from '../../api/modules/student';
import UploadField from '../../components/UploadField.vue';

const profile = reactive({});

onMounted(async () => {
  Object.assign(profile, await getMyProfile());
});

const save = async () => {
  await updateMyProfile(profile);
  ElMessage.success('保存成功');
};
</script>
