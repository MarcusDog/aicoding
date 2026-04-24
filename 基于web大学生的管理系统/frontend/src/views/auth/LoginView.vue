<template>
  <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px">
    <el-card style="width: 420px;border-radius:20px">
      <template #header>
        <div style="text-align:center">
          <div style="font-size:24px;font-weight:700;color:#143d63">上海立达学院</div>
          <div style="margin-top:8px;color:#5f7183">大学生志愿者管理系统</div>
        </div>
      </template>
      <el-form :model="form" label-position="top" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入学号或工号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" style="width:100%" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form>
      <div style="margin-top:16px;color:#6b7280;font-size:13px;line-height:1.8">
        默认演示账号：学生 `202209501` / 管理员 `A1001`，密码均为 `123456`
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const form = reactive({
  username: 'A1001',
  password: '123456'
});

const handleLogin = async () => {
  loading.value = true;
  try {
    await authStore.login(form);
    ElMessage.success('登录成功');
    router.push(authStore.user.roleCode === 'ADMIN' ? '/admin/dashboard' : '/student/home');
  } catch (error) {
    ElMessage.error(error.message || '登录失败');
  } finally {
    loading.value = false;
  }
};
</script>
