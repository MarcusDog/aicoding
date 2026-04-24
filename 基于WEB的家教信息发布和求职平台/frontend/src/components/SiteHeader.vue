<script setup>
import { computed } from 'vue'
import { roleText } from '../utils/format'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

defineEmits(['logout'])

const workspacePath = computed(() => {
  if (!props.user) {
    return '/login'
  }

  return {
    PARENT: '/parent',
    TUTOR: '/tutor',
    ADMIN: '/admin'
  }[props.user.role]
})
</script>

<template>
  <header class="site-header">
    <div class="topline">
      <p>衡阳地区家教供需撮合、教员审核与订单管理平台</p>
      <div v-if="user" class="header-user">
        <strong>{{ user.displayName }}</strong>
        <span>{{ roleText(user.role) }}</span>
      </div>
    </div>
    <div class="nav-row">
      <RouterLink class="brand" to="/">
        <span class="brand-mark">NH</span>
        <span>
          <strong>南华家教平台</strong>
          <small>家长、教员与管理端统一协同</small>
        </span>
      </RouterLink>
      <nav class="primary-nav" aria-label="主要导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/demands">家教需求</RouterLink>
        <RouterLink to="/tutors">教员信息</RouterLink>
        <RouterLink :to="workspacePath">工作台</RouterLink>
      </nav>
      <div class="header-actions">
        <template v-if="user">
          <RouterLink class="ghost-btn" :to="workspacePath">进入工作台</RouterLink>
          <button class="ghost-btn" type="button" @click="$emit('logout')">退出登录</button>
        </template>
        <template v-else>
          <RouterLink class="ghost-btn" to="/login">登录</RouterLink>
          <RouterLink class="solid-btn" to="/register">注册</RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>
