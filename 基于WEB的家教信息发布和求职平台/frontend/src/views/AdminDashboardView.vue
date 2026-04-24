<script setup>
import { onMounted, reactive, ref } from 'vue'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { useSession } from '../stores/session'
import { formatDate } from '../utils/format'

const { state } = useSession()

const loading = ref(true)
const errorMessage = ref('')
const notice = ref('')
const summary = ref(null)
const profiles = ref([])
const demands = ref([])
const applications = ref([])
const orders = ref([])
const audits = ref([])

const remarks = reactive({
  profiles: {},
  demands: {},
  applications: {}
})

async function loadWorkspace() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [dashboard, profileList, demandList, applicationList, orderList, auditList] = await Promise.all([
      api.dashboard(),
      api.adminProfiles(),
      api.adminDemands(),
      api.adminApplications(),
      api.adminOrders(),
      api.adminAudits()
    ])
    summary.value = dashboard
    profiles.value = profileList
    demands.value = demandList
    applications.value = applicationList
    orders.value = orderList
    audits.value = auditList
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

function remarkValue(scope, itemId, fallback) {
  if (!remarks[scope][itemId]) {
    remarks[scope][itemId] = fallback
  }
  return remarks[scope][itemId]
}

async function reviewProfile(profileId, approved) {
  errorMessage.value = ''
  notice.value = ''

  try {
    await api.auditProfile(state.user.id, profileId, {
      approved,
      remark: remarks.profiles[profileId] || (approved ? '资料符合要求' : '请补充更完整的资质材料')
    })
    notice.value = approved ? '教员资料已审核通过。' : '教员资料已驳回。'
    await loadWorkspace()
  } catch (error) {
    errorMessage.value = error.message
  }
}

async function reviewDemand(demandId, approved) {
  errorMessage.value = ''
  notice.value = ''

  try {
    await api.auditDemand(state.user.id, demandId, {
      approved,
      remark: remarks.demands[demandId] || (approved ? '需求信息完整' : '请补充更清晰的辅导要求')
    })
    notice.value = approved ? '家教需求已审核通过。' : '家教需求已驳回。'
    await loadWorkspace()
  } catch (error) {
    errorMessage.value = error.message
  }
}

async function reviewApplication(applicationId, approved) {
  errorMessage.value = ''
  notice.value = ''

  try {
    await api.reviewApplication(state.user.id, applicationId, {
      approved,
      remark: remarks.applications[applicationId] || (approved ? '教员与需求匹配，可进入服务阶段' : '暂不符合当前需求匹配条件')
    })
    notice.value = approved ? '接单申请已通过。' : '接单申请已驳回。'
    await loadWorkspace()
  } catch (error) {
    errorMessage.value = error.message
  }
}

onMounted(loadWorkspace)
</script>

<template>
  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">管理后台</p>
        <h1>{{ state.user.displayName }} 的审核工作台</h1>
      </div>
    </div>

    <p v-if="notice" class="success-text">{{ notice }}</p>
    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-if="summary" class="metrics-grid">
      <article class="metric-card">
        <strong>{{ summary.pendingTutorProfiles }}</strong>
        <span>待审教员资料</span>
      </article>
      <article class="metric-card">
        <strong>{{ summary.openDemands }}</strong>
        <span>开放需求</span>
      </article>
      <article class="metric-card">
        <strong>{{ summary.submittedApplications }}</strong>
        <span>待审申请</span>
      </article>
      <article class="metric-card">
        <strong>{{ summary.activeOrders }}</strong>
        <span>进行中订单</span>
      </article>
    </div>

    <div class="workspace-grid admin-grid">
      <section class="panel">
        <div class="page-title-row compact-row">
          <h2>教员资料审核</h2>
          <span class="muted">{{ profiles.length }} 条记录</span>
        </div>
        <div v-if="profiles.length" class="stack-list">
          <article v-for="profile in profiles" :key="profile.id" class="stack-item align-start">
            <div class="grow">
              <div class="inline-meta">
                <strong>{{ profile.userName }}</strong>
                <StatusBadge :status="profile.status" />
              </div>
              <p>{{ profile.school }} · {{ profile.major }} · {{ profile.subjects }}</p>
              <p class="helper-text">{{ profile.introduction }}</p>
              <label class="field">
                <span>审核备注</span>
                <textarea v-model="remarks.profiles[profile.id]" :placeholder="remarkValue('profiles', profile.id, profile.reviewRemark || '')" rows="2" />
              </label>
            </div>
            <div class="stack-actions">
              <RouterLink class="text-link" :to="`/tutors/${profile.id}`">查看资料</RouterLink>
              <button class="solid-btn" type="button" @click="reviewProfile(profile.id, true)">通过</button>
              <button class="ghost-btn danger-text" type="button" @click="reviewProfile(profile.id, false)">驳回</button>
            </div>
          </article>
        </div>
        <EmptyState
          v-else-if="!loading"
          title="没有教员资料记录"
          description="教员提交认证信息后，会进入这里等待审核。"
        />
      </section>

      <section class="panel">
        <div class="page-title-row compact-row">
          <h2>需求审核</h2>
          <span class="muted">{{ demands.length }} 条记录</span>
        </div>
        <div v-if="demands.length" class="stack-list">
          <article v-for="demand in demands" :key="demand.id" class="stack-item align-start">
            <div class="grow">
              <div class="inline-meta">
                <strong>{{ demand.title }}</strong>
                <StatusBadge :status="demand.status" />
              </div>
              <p>{{ demand.parentName }} · {{ demand.subject }} · {{ demand.gradeLevel }}</p>
              <p class="helper-text">{{ demand.description }}</p>
              <label class="field">
                <span>审核备注</span>
                <textarea v-model="remarks.demands[demand.id]" :placeholder="remarkValue('demands', demand.id, demand.reviewRemark || '')" rows="2" />
              </label>
            </div>
            <div class="stack-actions">
              <RouterLink class="text-link" :to="`/demands/${demand.id}`">查看需求</RouterLink>
              <button class="solid-btn" type="button" @click="reviewDemand(demand.id, true)">通过</button>
              <button class="ghost-btn danger-text" type="button" @click="reviewDemand(demand.id, false)">驳回</button>
            </div>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="page-title-row compact-row">
          <h2>接单申请审核</h2>
          <span class="muted">{{ applications.length }} 条记录</span>
        </div>
        <div v-if="applications.length" class="stack-list">
          <article v-for="item in applications" :key="item.id" class="stack-item align-start">
            <div class="grow">
              <div class="inline-meta">
                <strong>{{ item.demandTitle }}</strong>
                <StatusBadge :status="item.status" />
              </div>
              <p>教员：{{ item.tutorName }}</p>
              <p class="helper-text">{{ item.coverLetter }}</p>
              <label class="field">
                <span>审核备注</span>
                <textarea v-model="remarks.applications[item.id]" :placeholder="remarkValue('applications', item.id, item.reviewRemark || '')" rows="2" />
              </label>
            </div>
            <div class="stack-actions">
              <RouterLink class="text-link" :to="`/tutor-users/${item.tutorId}/profile`">查看教员</RouterLink>
              <RouterLink class="text-link" :to="`/demands/${item.demandId}`">查看需求</RouterLink>
              <button class="solid-btn" type="button" @click="reviewApplication(item.id, true)">通过</button>
              <button class="ghost-btn danger-text" type="button" @click="reviewApplication(item.id, false)">驳回</button>
            </div>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="page-title-row compact-row">
          <h2>订单与审核记录</h2>
          <span class="muted">{{ orders.length }} 个订单 / {{ audits.length }} 条记录</span>
        </div>

        <div class="stack-list">
          <article v-for="order in orders" :key="order.id" class="stack-item align-start">
            <div>
              <div class="inline-meta">
                <strong>{{ order.demandTitle }}</strong>
                <StatusBadge :status="order.status" />
              </div>
              <p>{{ order.parentName }} / {{ order.tutorName }}</p>
              <p class="helper-text">{{ formatDate(order.createdAt) }}</p>
            </div>
          </article>
        </div>

        <hr class="section-divider" />

        <div class="stack-list">
          <article v-for="audit in audits" :key="audit.id" class="stack-item align-start">
            <div>
              <div class="inline-meta">
                <strong>{{ audit.action }}</strong>
                <StatusBadge :status="audit.result" />
              </div>
              <p>{{ audit.reviewerName }} · {{ formatDate(audit.createdAt) }}</p>
              <p class="helper-text">{{ audit.remark }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>
