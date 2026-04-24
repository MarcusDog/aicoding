<template>
  <router-view v-if="isLoginPage" />
  <el-container v-else class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">Face Attendance</div>
      <el-menu :default-active="$route.path" router background-color="#1f2a37" text-color="#dbe4ef" active-text-color="#67e8f9">
        <el-menu-item index="/">看板</el-menu-item>
        <el-menu-item index="/users">员工管理</el-menu-item>
        <el-menu-item index="/attendance">考勤记录</el-menu-item>
        <el-menu-item index="/faces">人脸库</el-menu-item>
        <el-menu-item index="/rules">签到规则</el-menu-item>
        <el-menu-item index="/reports">统计报表</el-menu-item>
        <el-menu-item index="/logs">操作日志</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div>{{ auth.profile?.real_name || auth.profile?.username || "管理员" }}</div>
        <el-button type="danger" link @click="logout">退出登录</el-button>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getProfile } from "./api/auth";
import { useAuthStore } from "./store/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const isLoginPage = computed(() => route.path === "/login");

const loadProfile = async () => {
  if (!auth.isLoggedIn) return;
  try {
    const result = await getProfile();
    auth.setProfile(result.data.profile);
  } catch (error) {
    auth.clearToken();
    router.push("/login");
  }
};

const logout = () => {
  auth.clearToken();
  router.push("/login");
};

onMounted(loadProfile);
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.aside {
  background: linear-gradient(160deg, #1f2a37 0%, #132032 100%);
}

.logo {
  color: #67e8f9;
  font-size: 20px;
  font-weight: 700;
  padding: 20px 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.main {
  background: #f4f7fb;
}
</style>
