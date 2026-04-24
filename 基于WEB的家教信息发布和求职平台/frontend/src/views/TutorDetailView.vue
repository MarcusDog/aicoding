<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { formatDate } from '../utils/format'

const route = useRoute()
const loading = ref(true)
const errorMessage = ref('')
const profile = ref(null)

const isUserRoute = computed(() => Boolean(route.params.userId))

async function loadProfile() {
  loading.value = true
  errorMessage.value = ''

  try {
    profile.value = isUserRoute.value
      ? await api.tutorProfileByUser(route.params.userId)
      : await api.tutorProfileDetail(route.params.id)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <section class="page-section">
    <p v-if="loading" class="muted">正在加载教员资料...</p>
    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-if="profile" class="detail-grid">
      <article class="panel detail-panel">
        <div class="record-head">
          <div>
            <p class="eyebrow">教员详情</p>
            <h1>{{ profile.userName }}</h1>
            <p>{{ profile.school }} · {{ profile.major }} · {{ formatDate(profile.createdAt) }}</p>
          </div>
          <StatusBadge :status="profile.status" />
        </div>

        <div class="detail-list">
          <div>
            <span>学校</span>
            <strong>{{ profile.school }}</strong>
          </div>
          <div>
            <span>专业</span>
            <strong>{{ profile.major }}</strong>
          </div>
          <div>
            <span>可授科目</span>
            <strong>{{ profile.subjects }}</strong>
          </div>
          <div>
            <span>资料状态</span>
            <strong>{{ profile.status }}</strong>
          </div>
        </div>

        <section class="content-block">
          <h2>个人简介</h2>
          <p>{{ profile.introduction }}</p>
        </section>

        <section v-if="profile.reviewRemark" class="content-block remark-block">
          <h2>审核备注</h2>
          <p>{{ profile.reviewRemark }}</p>
        </section>
      </article>

      <aside class="panel sidebar-card">
        <h2>后续操作</h2>
        <p class="helper-text">家长可先在平台发布需求，管理员审核通过后，教员再进行申请接单。</p>
        <div class="stack-actions">
          <RouterLink class="solid-btn" to="/demands">查看家教需求</RouterLink>
          <RouterLink class="ghost-btn" to="/parent">发布需求</RouterLink>
        </div>
      </aside>
    </div>
  </section>
</template>
