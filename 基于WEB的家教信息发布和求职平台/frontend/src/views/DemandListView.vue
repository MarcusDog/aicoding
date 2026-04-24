<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { formatBudgetRange } from '../utils/format'

const demands = ref([])
const keyword = ref('')
const subject = ref('')
const loading = ref(true)
const errorMessage = ref('')

const subjectOptions = computed(() => {
  return [...new Set(demands.value.map((item) => item.subject))]
})

const filteredDemands = computed(() => {
  return demands.value.filter((item) => {
    const matchesKeyword = !keyword.value || [item.title, item.location, item.gradeLevel, item.description]
      .join(' ')
      .includes(keyword.value.trim())
    const matchesSubject = !subject.value || item.subject === subject.value
    return matchesKeyword && matchesSubject
  })
})

async function loadDemands() {
  loading.value = true
  errorMessage.value = ''

  try {
    demands.value = await api.catalogDemands()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(loadDemands)
</script>

<template>
  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">家教需求大厅</p>
        <h1>浏览当前开放的家教需求</h1>
      </div>
      <RouterLink class="ghost-btn" to="/register">家长发布需求</RouterLink>
    </div>

    <div class="panel filter-bar">
      <label class="field grow">
        <span>关键词</span>
        <input v-model="keyword" placeholder="按标题、地区、年级或描述筛选" />
      </label>
      <label class="field">
        <span>科目</span>
        <select v-model="subject">
          <option value="">全部科目</option>
          <option v-for="item in subjectOptions" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </div>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="loading" class="muted">正在加载需求列表...</p>

    <div v-if="filteredDemands.length" class="record-grid">
      <article v-for="item in filteredDemands" :key="item.id" class="record-card">
        <div class="record-head">
          <div>
            <h2>{{ item.title }}</h2>
            <p>{{ item.parentName }} 发布 · {{ item.subject }} · {{ item.gradeLevel }}</p>
          </div>
          <StatusBadge :status="item.status" />
        </div>
        <p class="record-summary">{{ item.description }}</p>
        <div class="record-meta multi-line">
          <span>授课地点：{{ item.location }}</span>
          <span>上课时间：{{ item.schedule }}</span>
          <span>课时预算：{{ formatBudgetRange(item) }}</span>
        </div>
        <RouterLink class="text-link" :to="`/demands/${item.id}`">查看详情</RouterLink>
      </article>
    </div>

    <EmptyState
      v-else-if="!loading"
      title="没有符合条件的需求"
      description="请调整筛选条件，或等待新的家教需求通过审核后上线。"
    />
  </section>
</template>
