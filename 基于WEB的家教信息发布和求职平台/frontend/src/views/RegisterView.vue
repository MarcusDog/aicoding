<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useSession } from '../stores/session'

const router = useRouter()
const { setUser } = useSession()

const form = reactive({
  username: '',
  password: '',
  displayName: '',
  phone: '',
  role: 'PARENT'
})

const loading = ref(false)
const errorMessage = ref('')

async function submit() {
  loading.value = true
  errorMessage.value = ''

  try {
    const user = await api.register(form)
    setUser(user)
    await router.push(user.role === 'PARENT' ? '/parent' : '/tutor')
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
        <p class="eyebrow">账号注册</p>
        <h1>创建平台账号</h1>
      </div>
      <RouterLink class="text-link" to="/login">已有账号？去登录</RouterLink>
    </div>

    <form class="panel form-panel" @submit.prevent="submit">
      <div class="form-grid two">
        <label class="field">
          <span>用户名</span>
          <input v-model="form.username" autocomplete="username" placeholder="建议使用拼音或英文" />
        </label>
        <label class="field">
          <span>登录密码</span>
          <input v-model="form.password" type="password" autocomplete="new-password" placeholder="至少 6 位" />
        </label>
        <label class="field">
          <span>姓名</span>
          <input v-model="form.displayName" placeholder="请输入真实姓名" />
        </label>
        <label class="field">
          <span>手机号码</span>
          <input v-model="form.phone" inputmode="tel" placeholder="请输入联系电话" />
        </label>
      </div>

      <label class="field">
        <span>注册角色</span>
        <select v-model="form.role">
          <option value="PARENT">家长</option>
          <option value="TUTOR">教员</option>
        </select>
      </label>

      <p class="helper-text">家长注册后可直接发布需求；教员注册后需先提交资料并等待管理员审核。</p>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <button class="solid-btn" :disabled="loading" type="submit">
        {{ loading ? '提交中...' : '完成注册' }}
      </button>
    </form>
  </section>
</template>
