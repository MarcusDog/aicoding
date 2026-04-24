<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useSession } from '../stores/session'
import { roleText } from '../utils/format'

const route = useRoute()
const router = useRouter()
const { setUser } = useSession()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

const demoAccounts = [
  { username: 'parent', password: '123456', role: 'PARENT', label: '家长演示账号' },
  { username: 'tutor', password: '123456', role: 'TUTOR', label: '教员演示账号' },
  { username: 'admin', password: '123456', role: 'ADMIN', label: '管理员演示账号' }
]

const redirectPath = computed(() => route.query.redirect || '')

function workspacePath(role) {
  return {
    PARENT: '/parent',
    TUTOR: '/tutor',
    ADMIN: '/admin'
  }[role] || '/'
}

function fillDemo(account) {
  form.username = account.username
  form.password = account.password
}

async function submit() {
  loading.value = true
  errorMessage.value = ''

  try {
    const user = await api.login(form.username, form.password)
    setUser(user)
    await router.push(redirectPath.value || workspacePath(user.role))
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-section narrow">
    <div class="page-title-row">
      <div>
        <p class="eyebrow">账号登录</p>
        <h1>进入平台工作台</h1>
      </div>
      <RouterLink class="text-link" to="/register">没有账号？去注册</RouterLink>
    </div>

    <div class="two-column">
      <form class="panel form-panel" @submit.prevent="submit">
        <label class="field">
          <span>用户名</span>
          <input v-model="form.username" autocomplete="username" placeholder="请输入用户名" />
        </label>
        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <button class="solid-btn full-width" :disabled="loading" type="submit">
          {{ loading ? '登录中...' : '登录系统' }}
        </button>
      </form>

      <div class="panel">
        <h2>演示账号</h2>
        <p class="helper-text">为便于演示答辩，系统预置了三个角色账号。点击“填入”后可直接登录对应工作台。</p>
        <div class="stack-list">
          <div v-for="account in demoAccounts" :key="account.username" class="stack-item">
            <div>
              <strong>{{ account.label }}</strong>
              <p>{{ account.username }} / {{ account.password }} · {{ roleText(account.role) }}</p>
            </div>
            <button class="ghost-btn" type="button" @click="fillDemo(account)">填入</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
