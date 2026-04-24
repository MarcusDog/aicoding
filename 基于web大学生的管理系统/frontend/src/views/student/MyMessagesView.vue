<template>
  <el-card>
    <template #header>我的消息</template>
    <el-timeline>
      <el-timeline-item v-for="msg in messages" :key="msg.id" :timestamp="msg.createdAt">
        <el-tag :type="msg.isRead ? 'info' : 'danger'" style="margin-right:8px">{{ msg.messageType }}</el-tag>
        <strong>{{ msg.title }}</strong>
        <div style="margin-top:8px">{{ msg.content }}</div>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { getMyMessages } from '../../api/modules/student';

const messages = ref([]);

onMounted(async () => {
  messages.value = await getMyMessages();
});
</script>
