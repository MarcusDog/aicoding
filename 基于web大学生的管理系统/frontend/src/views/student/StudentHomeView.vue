<template>
  <div>
    <div class="card-grid">
      <el-card>
        <div>累计时长</div>
        <h2>{{ home.summary?.totalServiceHours || 0 }} 小时</h2>
      </el-card>
      <el-card>
        <div>我的报名</div>
        <h2>{{ home.summary?.signupCount || 0 }}</h2>
      </el-card>
      <el-card>
        <div>未读消息</div>
        <h2>{{ home.summary?.unreadCount || 0 }}</h2>
      </el-card>
      <el-card>
        <div>当前身份</div>
        <h2>学生志愿者</h2>
      </el-card>
    </div>

    <div class="chart-grid">
      <el-card>
        <template #header>近期活动</template>
        <el-table :data="home.recentActivities || []" border>
          <el-table-column prop="title" label="活动名称" />
          <el-table-column prop="location" label="地点" />
          <el-table-column prop="activityStatus" label="状态" />
        </el-table>
      </el-card>
      <el-card>
        <template #header>系统公告</template>
        <el-timeline>
          <el-timeline-item
            v-for="notice in home.notices || []"
            :key="notice.id"
            :timestamp="notice.publishedAt"
          >
            {{ notice.title }}
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import { getStudentHome } from '../../api/modules/student';

const home = reactive({});

onMounted(async () => {
  Object.assign(home, await getStudentHome());
});
</script>
