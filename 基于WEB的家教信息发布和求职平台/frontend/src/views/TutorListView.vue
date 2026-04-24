<script setup>
import { computed, onMounted, ref } from 'vue'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'

const profiles = ref([])
const loading = ref(true)
const errorMessage = ref('')
const keyword = ref('')

const filteredProfiles = computed(() => {
  return profiles.value.filter((profile) => {
    return [profile.userName, profile.school, profile.major, profile.subjects, profile.introduction]
      .join(' ')
      .includes(keyword.value.trim())
  })
})

async function loadProfiles() {
  loading.value = true
  errorMessage.value = ''

  try {
    profiles.value = await api.approvedTutors()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(loadProfiles)
</script>

<template>
  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">教员信息展示</p>
        <h1>认证通过的教员资料</h1>
      </div>
      <RouterLink class="ghost-btn" to="/register">注册教员</RouterLink>
    </div>

    <div class="panel filter-bar">
      <label class="field grow">
        <span>关键词</span>
        <input v-model="keyword" placeholder="按姓名、学校、专业或科目筛选" />
      </label>
    </div>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="loading" class="muted">正在加载教员资料...</p>

    <div v-if="filteredProfiles.length" class="record-grid">
      <article v-for="profile in filteredProfiles" :key="profile.id" class="record-card">
        <div class="record-head">
          <div>
            <h2>{{ profile.userName }}</h2>
            <p>{{ profile.school }} · {{ profile.major }}</p>
          </div>
          <StatusBadge :status="profile.status" />
        </div>
        <p class="record-summary">{{ profile.introduction }}</p>
        <div class="tag-row">
          <span v-for="subject in profile.subjects.split(',')" :key="subject" class="plain-tag">{{ subject.trim() }}</span>
        </div>
        <RouterLink class="text-link" :to="`/tutors/${profile.id}`">查看详细资料</RouterLink>
      </article>
    </div>

    <EmptyState
      v-else-if="!loading"
      title="暂无可展示的教员资料"
      description="等待教员提交资料并通过管理员审核后，这里会显示认证结果。"
    />
  </section>
</template>
