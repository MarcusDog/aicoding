<template>
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card>
        <template #header>签到</template>
        <el-form label-position="top">
          <el-form-item label="活动 ID">
            <el-input v-model="signInForm.activityId" />
          </el-form-item>
          <el-form-item label="签到码">
            <el-input v-model="signInForm.code" />
          </el-form-item>
          <el-button type="primary" @click="handleSignIn">提交签到</el-button>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card>
        <template #header>签退</template>
        <el-form label-position="top">
          <el-form-item label="活动 ID">
            <el-input v-model="signOutForm.activityId" />
          </el-form-item>
          <el-form-item label="签退码">
            <el-input v-model="signOutForm.code" />
          </el-form-item>
          <el-button type="success" @click="handleSignOut">提交签退</el-button>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { signIn, signOut } from '../../api/modules/student';

const signInForm = reactive({ activityId: '', code: '' });
const signOutForm = reactive({ activityId: '', code: '' });

const handleSignIn = async () => {
  await signIn({ activityId: Number(signInForm.activityId), code: signInForm.code });
  ElMessage.success('签到成功');
};

const handleSignOut = async () => {
  await signOut({ activityId: Number(signOutForm.activityId), code: signOutForm.code });
  ElMessage.success('签退成功');
};
</script>
