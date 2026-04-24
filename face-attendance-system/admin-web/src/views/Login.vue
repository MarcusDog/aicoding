<template>
  <div class="login-page">
    <el-card class="card">
      <h2>管理员登录</h2>
      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item label="账号">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="onSubmit" style="width: 100%">登录</el-button>
      </el-form>
      <p class="tips">默认账号：admin / admin123</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";

import { adminLogin } from "../api/auth";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);

const form = reactive({
  username: "admin",
  password: "admin123",
});

const onSubmit = async () => {
  loading.value = true;
  try {
    const result = await adminLogin(form);
    auth.setToken(result.data.token);
    auth.setProfile(result.data.admin);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (error) {
    ElMessage.error(error.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at top left, #67e8f9 0%, #0f172a 55%);
}

.card {
  width: 380px;
  border-radius: 16px;
}

h2 {
  margin: 0 0 20px;
}

.tips {
  margin-top: 12px;
  color: #64748b;
  font-size: 12px;
}
</style>
