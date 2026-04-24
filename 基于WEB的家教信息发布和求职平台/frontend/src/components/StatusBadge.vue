<script setup>
import { computed } from 'vue'
import { statusText } from '../utils/format'

const props = defineProps({
  status: {
    type: String,
    default: ''
  }
})

const badgeClass = computed(() => {
  return {
    'status-badge': true,
    'is-success': ['APPROVED', 'OPEN', 'ACTIVE', 'ACCEPTED'].includes(props.status),
    'is-pending': ['PENDING', 'PENDING_REVIEW', 'SUBMITTED'].includes(props.status),
    'is-warning': ['MATCHED'].includes(props.status),
    'is-danger': ['REJECTED'].includes(props.status)
  }
})
</script>

<template>
  <span :class="badgeClass">{{ statusText(status) }}</span>
</template>
