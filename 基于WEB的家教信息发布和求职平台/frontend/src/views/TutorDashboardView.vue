<script setup>
import { onMounted, reactive, ref } from 'vue'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { api } from '../api'
import { useSession } from '../stores/session'
import { formatBudgetRange, formatDate } from '../utils/format'

const { state } = useSession()

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const notice = ref('')
const profile = ref(null)
const openDemands = ref([])
const applications = ref([])
const orders = ref([])
const editingRejectedProfile = ref(false)

const form = reactive({
  school: '南华大学',
  major: '',
  subjects: '',
  introduction: ''
})

function resetProfileForm() {
  editingRejectedProfile.value = false
  form.school = '南华大学'
  form.major = ''
  form.subjects = ''
  form.introduction = ''
}

function startReviseProfile() {
  if (!profile.value) {
    return
  }
  editingRejectedProfile.value = true
  form.school = profile.value.school
  form.major = profile.value.major
  form.subjects = profile.value.subjects
  form.introduction = profile.value.introduction
  notice.value = '已载入被驳回资料，请按审核备注修改后重新提交。'
}

async function loadProfile() {
  try {
    profile.value = await api.tutorProfile(state.user.id)
  } catch {
    profile.value = null
  }
}

async function loadWorkspace() {
  loading.value = true
  errorMessage.value = ''

  try {
    await loadProfile()
    const [demandList, applicationList, orderList] = await Promise.all([
      api.openDemands(),
      api.tutorApplications(state.user.id),
      api.tutorOrders(state.user.id)
    ])
    openDemands.value = demandList
    applications.value = applicationList
    orders.value = orderList
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function submitProfile() {
  saving.value = true
  errorMessage.value = ''
  notice.value = ''

  try {
    if (editingRejectedProfile.value) {
      profile.value = await api.resubmitTutorProfile(state.user.id, form)
      notice.value = '资料已重新提交，请等待管理员复审。'
    } else {
      profile.value = await api.submitTutorProfile(state.user.id, form)
      notice.value = '资料已提交，请等待管理员审核。'
    }
    resetProfileForm()
    await loadWorkspace()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

onMounted(loadWorkspace)
</script>

<template>
  <section class="page-section">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">教员工作台</p>
        <h1>{{ state.user.displayName }} 的接单管理</h1>
      </div>
    </div>

    <div class="workspace-grid">
      <section class="panel">
        <div class="page-title-row compact-row">
          <h2>认证资料</h2>
          <StatusBadge v-if="profile" :status="profile.status" />
        </div>

        <template v-if="profile && !editingRejectedProfile">
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
              <span>科目</span>
              <strong>{{ profile.subjects }}</strong>
            </div>
            <div>
              <span>提交时间</span>
              <strong>{{ formatDate(profile.createdAt) }}</strong>
            </div>
          </div>
          <p class="helper-text">{{ profile.introduction }}</p>
          <p v-if="profile.reviewRemark" :class="profile.status === 'REJECTED' ? 'error-text' : 'helper-text'">
            审核备注：{{ profile.reviewRemark }}
          </p>
          <button
            v-if="profile.status === 'REJECTED'"
            class="solid-btn"
            type="button"
            @click="startReviseProfile"
          >
            修改资料并重新提交
          </button>
        </template>
        <template v-else>
          <form class="form-panel" @submit.prevent="submitProfile">
            <div class="page-title-row compact-row">
              <h3>{{ editingRejectedProfile ? '重新提交认证资料' : '提交认证资料' }}</h3>
              <button v-if="editingRejectedProfile" class="ghost-btn" type="button" @click="resetProfileForm">取消修改</button>
            </div>
            <div class="form-grid two">
              <label class="field">
                <span>学校</span>
                <input v-model="form.school" />
              </label>
              <label class="field">
                <span>专业</span>
                <input v-model="form.major" placeholder="例如：物理学" />
              </label>
            </div>
            <label class="field">
              <span>可授科目</span>
              <input v-model="form.subjects" placeholder="例如：数学,物理" />
            </label>
            <label class="field">
              <span>个人简介</span>
              <textarea v-model="form.introduction" rows="5" placeholder="填写辅导经验、擅长方向和授课风格" />
            </label>
            <p v-if="notice" class="success-text">{{ notice }}</p>
            <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
            <button class="solid-btn" :disabled="saving" type="submit">
              {{ saving ? '提交中...' : editingRejectedProfile ? '修改后重新提交' : '提交认证资料' }}
            </button>
          </form>
        </template>
      </section>

      <div class="stack-layout">
        <section class="panel">
          <div class="page-title-row compact-row">
            <h2>开放需求</h2>
            <span class="muted">{{ openDemands.length }} 条记录</span>
          </div>
          <p v-if="loading" class="muted">正在读取需求...</p>
          <div v-if="openDemands.length" class="stack-list">
            <article v-for="item in openDemands" :key="item.id" class="stack-item align-start">
              <div class="grow">
                <div class="inline-meta">
                  <strong>{{ item.title }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p>{{ item.subject }} · {{ item.gradeLevel }} · {{ item.location }}</p>
                <p class="helper-text">{{ formatBudgetRange(item) }} · {{ item.schedule }}</p>
              </div>
              <RouterLink class="text-link" :to="`/demands/${item.id}`">查看详情</RouterLink>
            </article>
          </div>
          <EmptyState
            v-else-if="!loading"
            title="当前没有可申请的需求"
            description="管理员审核通过的需求会自动展示在这里。"
          />
        </section>

        <section class="panel">
          <div class="page-title-row compact-row">
            <h2>我的申请</h2>
            <span class="muted">{{ applications.length }} 条记录</span>
          </div>
          <div v-if="applications.length" class="stack-list">
            <article v-for="item in applications" :key="item.id" class="stack-item align-start">
              <div class="grow">
                <div class="inline-meta">
                  <strong>{{ item.demandTitle }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p class="helper-text">{{ item.coverLetter }}</p>
                <p v-if="item.reviewRemark" class="error-text">审核备注：{{ item.reviewRemark }}</p>
              </div>
              <RouterLink class="text-link" :to="`/demands/${item.demandId}`">对应需求</RouterLink>
            </article>
          </div>
          <EmptyState
            v-else
            title="还没有提交申请"
            description="从开放需求列表进入详情页后，可以提交接单申请。"
          />
        </section>

        <section class="panel">
          <div class="page-title-row compact-row">
            <h2>我的订单</h2>
            <span class="muted">{{ orders.length }} 条记录</span>
          </div>
          <div v-if="orders.length" class="stack-list">
            <article v-for="order in orders" :key="order.id" class="stack-item align-start">
              <div>
                <div class="inline-meta">
                  <strong>{{ order.demandTitle }}</strong>
                  <StatusBadge :status="order.status" />
                </div>
                <p>家长：{{ order.parentName }}</p>
                <p class="helper-text">创建时间：{{ formatDate(order.createdAt) }}</p>
              </div>
            </article>
          </div>
          <EmptyState
            v-else
            title="当前没有订单"
            description="管理员通过你的申请后，订单信息会同步到这里。"
          />
        </section>
      </div>
    </div>
  </section>
</template>
