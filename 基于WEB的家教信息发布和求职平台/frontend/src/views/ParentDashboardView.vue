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
const demands = ref([])
const orders = ref([])
const editingDemandId = ref(null)

const form = reactive({
  title: '',
  subject: '数学',
  gradeLevel: '初中',
  location: '衡阳市蒸湘区',
  budgetMin: 120,
  budgetMax: 180,
  schedule: '周六下午',
  description: ''
})

function resetForm() {
  editingDemandId.value = null
  form.title = ''
  form.subject = '数学'
  form.gradeLevel = '初中'
  form.location = '衡阳市蒸湘区'
  form.budgetMin = 120
  form.budgetMax = 180
  form.schedule = '周六下午'
  form.description = ''
}

function startReviseDemand(item) {
  editingDemandId.value = item.id
  form.title = item.title
  form.subject = item.subject
  form.gradeLevel = item.gradeLevel
  form.location = item.location
  form.budgetMin = item.budgetMin
  form.budgetMax = item.budgetMax
  form.schedule = item.schedule
  form.description = item.description
  notice.value = '已载入被驳回需求，请按审核备注修改后重新提交。'
}

async function loadWorkspace() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [demandList, orderList] = await Promise.all([
      api.parentDemands(state.user.id),
      api.parentOrders(state.user.id)
    ])
    demands.value = demandList
    orders.value = orderList
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function publishDemand() {
  saving.value = true
  errorMessage.value = ''
  notice.value = ''

  try {
    if (editingDemandId.value) {
      await api.resubmitDemand(state.user.id, editingDemandId.value, form)
      notice.value = '需求已重新提交，等待管理员复审。'
    } else {
      await api.publishDemand(state.user.id, form)
      notice.value = '需求已提交，等待管理员审核。'
    }
    resetForm()
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
        <p class="eyebrow">家长工作台</p>
        <h1>{{ state.user.displayName }} 的需求管理</h1>
      </div>
    </div>

    <div class="workspace-grid">
      <form class="panel form-panel" @submit.prevent="publishDemand">
        <div class="page-title-row compact-row">
          <h2>{{ editingDemandId ? '修改被驳回需求' : '发布新需求' }}</h2>
          <button v-if="editingDemandId" class="ghost-btn" type="button" @click="resetForm">取消修改</button>
        </div>
        <div class="form-grid two">
          <label class="field">
            <span>需求标题</span>
            <input v-model="form.title" placeholder="例如：初二英语语法专项辅导" />
          </label>
          <label class="field">
            <span>授课科目</span>
            <input v-model="form.subject" />
          </label>
          <label class="field">
            <span>学生年级</span>
            <input v-model="form.gradeLevel" />
          </label>
          <label class="field">
            <span>授课地点</span>
            <input v-model="form.location" />
          </label>
          <label class="field">
            <span>预算下限</span>
            <input v-model.number="form.budgetMin" min="0" step="10" type="number" />
          </label>
          <label class="field">
            <span>预算上限</span>
            <input v-model.number="form.budgetMax" min="0" step="10" type="number" />
          </label>
        </div>
        <label class="field">
          <span>上课时间</span>
          <input v-model="form.schedule" placeholder="例如：周三晚上、周六上午" />
        </label>
        <label class="field">
          <span>需求描述</span>
          <textarea v-model="form.description" rows="5" placeholder="请填写学生基础、辅导目标与其他要求" />
        </label>
        <p v-if="notice" class="success-text">{{ notice }}</p>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <button class="solid-btn" :disabled="saving" type="submit">
          {{ saving ? '提交中...' : editingDemandId ? '修改后重新提交' : '提交审核' }}
        </button>
      </form>

      <div class="stack-layout">
        <section class="panel">
          <div class="page-title-row compact-row">
            <h2>我的需求</h2>
            <span class="muted">{{ demands.length }} 条记录</span>
          </div>
          <p v-if="loading" class="muted">正在读取需求...</p>
          <div v-if="demands.length" class="stack-list">
            <article v-for="item in demands" :key="item.id" class="stack-item align-start">
              <div class="grow">
                <div class="inline-meta">
                  <strong>{{ item.title }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p>{{ item.subject }} · {{ item.gradeLevel }} · {{ formatBudgetRange(item) }}</p>
                <p class="helper-text">{{ item.description }}</p>
                <p v-if="item.reviewRemark" class="error-text">审核备注：{{ item.reviewRemark }}</p>
              </div>
              <RouterLink class="text-link" :to="`/demands/${item.id}`">查看详情</RouterLink>
              <button
                v-if="item.status === 'REJECTED'"
                class="ghost-btn"
                type="button"
                @click="startReviseDemand(item)"
              >
                修改后重新提交
              </button>
            </article>
          </div>
          <EmptyState
            v-else-if="!loading"
            title="还没有发布需求"
            description="填写左侧表单并提交审核后，需求会显示在这里。"
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
                <p>教员：{{ order.tutorName }}</p>
                <p class="helper-text">创建时间：{{ formatDate(order.createdAt) }}</p>
              </div>
            </article>
          </div>
          <EmptyState
            v-else
            title="当前没有订单"
            description="当管理员审核通过教员申请后，订单会自动出现在这里。"
          />
        </section>
      </div>
    </div>
  </section>
</template>
