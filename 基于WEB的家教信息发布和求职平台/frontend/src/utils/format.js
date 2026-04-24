export function formatCurrency(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0
  }).format(value ?? 0)
}

export function formatBudgetRange(item) {
  return `${formatCurrency(item.budgetMin)} - ${formatCurrency(item.budgetMax)} / 小时`
}

export function formatDate(value) {
  if (!value) {
    return '暂无时间'
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

export function statusText(status) {
  return {
    ACTIVE: '进行中',
    APPROVED: '已通过',
    MATCHED: '已匹配',
    OPEN: '开放中',
    PENDING: '待审核',
    PENDING_REVIEW: '待审核',
    REJECTED: '已驳回',
    SUBMITTED: '待处理',
    ACCEPTED: '已通过'
  }[status] || status
}

export function roleText(role) {
  return {
    PARENT: '家长',
    TUTOR: '教员',
    ADMIN: '管理员'
  }[role] || role
}
