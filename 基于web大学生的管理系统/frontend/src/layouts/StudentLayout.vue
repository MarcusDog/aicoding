<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #0f4c5c; color: #fff">
      <div style="padding: 24px 20px; font-size: 18px; font-weight: 700">学生志愿者门户</div>
      <el-menu
        :default-active="$route.path"
        background-color="#0f4c5c"
        text-color="#d8f0f4"
        active-text-color="#ffffff"
        router
      >
        <el-menu-item index="/student/home">首页</el-menu-item>
        <el-menu-item index="/student/activities">活动中心</el-menu-item>
        <el-menu-item index="/student/signups">我的报名</el-menu-item>
        <el-menu-item index="/student/checkin">签到签退</el-menu-item>
        <el-menu-item index="/student/hours">我的时长</el-menu-item>
        <el-menu-item index="/student/messages">我的消息</el-menu-item>
        <el-menu-item index="/student/profile">个人中心</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-bottom:1px solid #e5edf5">
        <div>{{ authStore.user?.displayName }} / 学生</div>
        <el-button type="danger" plain @click="logout">退出登录</el-button>
      </el-header>
      <el-main class="page-container">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>
