<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { formatBudgetRange } from '../utils/format'

const loading = ref(true)
const errorMessage = ref('')
const dashboard = ref(null)
const demands = ref([])
const tutors = ref([])

async function loadHome() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [summary, demandList, tutorList] = await Promise.all([
      api.dashboard(),
      api.catalogDemands(),
      api.approvedTutors()
    ])

    dashboard.value = summary
    demands.value = demandList.slice(0, 4)
    tutors.value = tutorList.slice(0, 4)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

onMounted(loadHome)
</script>

<template>
  <section class="hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">本地家教业务平台</p>
      <h1>用正常的网站流程完成家教撮合、资料审核和订单管理。</h1>
      <p class="hero-text">
        家长可以发布需求并查看审核结果，教员可以提交资料、浏览开放需求并申请接单，管理员统一处理认证、需求与申请审核。
      </p>
      <div class="action-cluster">
        <RouterLink class="solid-btn" to="/demands">查看家教需求</RouterLink>
        <RouterLink class="ghost-btn" to="/register">注册账号</RouterLink>
      </div>
    </div>
    <aside class="hero-panel">
      <h2>当前平台概况</h2>
      <p>系统数据来自真实后端接口，以下数字与工作台列表同步刷新。</p>
      <div v-if="dashboard" class="metrics-grid compact">
        <article class="metric-card">
          <strong>{{ dashboard.parents }}</strong>
          <span>家长账号</span>
        </article>
        <article class="metric-card">
          <strong>{{ dashboard.tutors }}</strong>
          <span>教员账号</span>
        </article>
        <article class="metric-card">
          <strong>{{ dashboard.openDemands }}</strong>
          <span>开放需求</span>
        </article>
        <article class="metric-card">
          <strong>{{ dashboard.activeOrders }}</strong>
          <span>进行中订单</span>
        </article>
      </div>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p v-if="loading" class="muted">正在读取首页数据...</p>
    </aside>
  </section>

  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">最新需求</p>
        <h2>开放中的家教需求</h2>
      </div>
      <RouterLink class="text-link" to="/demands">查看全部</RouterLink>
    </div>
    <div v-if="demands.length" class="record-grid">
      <article v-for="item in demands" :key="item.id" class="record-card">
        <div class="record-head">
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.subject }} · {{ item.gradeLevel }} · {{ item.location }}</p>
          </div>
          <StatusBadge :status="item.status" />
        </div>
        <p class="record-summary">{{ item.description }}</p>
        <div class="record-meta">
          <span>{{ formatBudgetRange(item) }}</span>
          <span>{{ item.schedule }}</span>
        </div>
        <RouterLink class="text-link" :to="`/demands/${item.id}`">查看需求详情</RouterLink>
      </article>
    </div>
    <EmptyState
      v-else-if="!loading"
      title="暂时没有开放需求"
      description="家长发布并通过审核后，需求会在这里展示。"
    />
  </section>

  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">已通过认证</p>
        <h2>教员资料展示</h2>
      </div>
      <RouterLink class="text-link" to="/tutors">查看全部</RouterLink>
    </div>
    <div v-if="tutors.length" class="record-grid">
      <article v-for="profile in tutors" :key="profile.id" class="record-card">
        <div class="record-head">
          <div>
            <h3>{{ profile.userName }}</h3>
            <p>{{ profile.school }} · {{ profile.major }}</p>
          </div>
          <StatusBadge :status="profile.status" />
        </div>
        <p class="record-summary">{{ profile.introduction }}</p>
        <div class="tag-row">
          <span v-for="subject in profile.subjects.split(',')" :key="subject" class="plain-tag">{{ subject.trim() }}</span>
        </div>
        <RouterLink class="text-link" :to="`/tutors/${profile.id}`">查看教员详情</RouterLink>
      </article>
    </div>
    <EmptyState
      v-else-if="!loading"
      title="当前没有可展示教员"
      description="教员资料通过管理员审核后会展示在此页面。"
    />
  </section>
</template>
