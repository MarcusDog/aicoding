<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { useSession } from '../stores/session'
import { formatBudgetRange, formatDate } from '../utils/format'

const route = useRoute()
const { state } = useSession()

const demand = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const notice = ref('')
const applying = ref(false)
const coverLetter = ref('我可以根据学生当前基础制定分阶段辅导计划，并在首节课后给出学习建议。')

const canApply = computed(() => state.user?.role === 'TUTOR')

async function loadDemand() {
  loading.value = true
  errorMessage.value = ''

  try {
    demand.value = await api.demandDetail(route.params.id)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function apply() {
  if (!state.user || !demand.value) {
    return
  }

  applying.value = true
  errorMessage.value = ''
  notice.value = ''

  try {
    await api.applyForDemand(state.user.id, {
      demandId: demand.value.id,
      coverLetter: coverLetter.value
    })
    notice.value = '接单申请已提交，管理员审核后会在教员工作台显示结果。'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    applying.value = false
  }
}

onMounted(loadDemand)
</script>

<template>
  <section class="page-section">
    <p v-if="loading" class="muted">正在加载需求详情...</p>
    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-if="demand" class="detail-grid">
      <article class="panel detail-panel">
        <div class="record-head">
          <div>
            <p class="eyebrow">需求详情</p>
            <h1>{{ demand.title }}</h1>
            <p>{{ demand.parentName }} 发布 · {{ formatDate(demand.createdAt) }}</p>
          </div>
          <StatusBadge :status="demand.status" />
        </div>

        <div class="detail-list">
          <div>
            <span>科目</span>
            <strong>{{ demand.subject }}</strong>
          </div>
          <div>
            <span>年级</span>
            <strong>{{ demand.gradeLevel }}</strong>
          </div>
          <div>
            <span>授课地点</span>
            <strong>{{ demand.location }}</strong>
          </div>
          <div>
            <span>上课时间</span>
            <strong>{{ demand.schedule }}</strong>
          </div>
          <div>
            <span>课时预算</span>
            <strong>{{ formatBudgetRange(demand) }}</strong>
          </div>
        </div>

        <section class="content-block">
          <h2>需求描述</h2>
          <p>{{ demand.description }}</p>
        </section>

        <section v-if="demand.reviewRemark" class="content-block remark-block">
          <h2>审核备注</h2>
          <p>{{ demand.reviewRemark }}</p>
        </section>
      </article>

      <aside class="panel sidebar-card">
        <h2>教员申请</h2>
        <p class="helper-text">教员认证通过后，可针对开放中的需求提交申请说明。</p>

        <template v-if="canApply && demand.status === 'OPEN'">
          <label class="field">
            <span>申请说明</span>
            <textarea v-model="coverLetter" rows="6" />
          </label>
          <p v-if="notice" class="success-text">{{ notice }}</p>
          <button class="solid-btn full-width" :disabled="applying" type="button" @click="apply">
            {{ applying ? '提交中...' : '提交接单申请' }}
          </button>
        </template>
        <template v-else-if="canApply">
          <p class="helper-text">该需求当前不处于开放状态，暂时不能申请。</p>
        </template>
        <template v-else>
          <p class="helper-text">如需申请该需求，请先使用教员账号登录；家长可在工作台中发布自己的新需求。</p>
          <div class="stack-actions">
            <RouterLink class="ghost-btn" to="/login">教员登录</RouterLink>
            <RouterLink class="ghost-btn" to="/register">注册教员账号</RouterLink>
          </div>
        </template>
      </aside>
    </div>
  </section>
</template>
