<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #123b62; color: #fff">
      <div style="padding: 24px 20px; font-size: 18px; font-weight: 700">志愿者管理后台</div>
      <el-menu
        :default-active="$route.path"
        background-color="#123b62"
        text-color="#d8e7f5"
        active-text-color="#ffffff"
        router
      >
        <el-menu-item index="/admin/dashboard">数据看板</el-menu-item>
        <el-menu-item index="/admin/students">学生管理</el-menu-item>
        <el-menu-item index="/admin/activities">活动管理</el-menu-item>
        <el-menu-item index="/admin/signups">报名审核</el-menu-item>
        <el-menu-item index="/admin/signs">签到管理</el-menu-item>
        <el-menu-item index="/admin/hours">时长认定</el-menu-item>
        <el-menu-item index="/admin/notices">公告管理</el-menu-item>
        <el-menu-item index="/admin/reports">统计报表</el-menu-item>
        <el-menu-item index="/admin/admins">管理员管理</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-bottom:1px solid #e5edf5">
        <div>{{ authStore.user?.displayName }} / 管理员</div>
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
