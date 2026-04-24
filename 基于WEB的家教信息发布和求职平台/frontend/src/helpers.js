export const roleText = {
  PARENT: '家长',
  TUTOR: '教员',
  ADMIN: '管理员'
};

export const statusText = {
  ACTIVE: '进行中',
  APPROVED: '已通过',
  ACCEPTED: '已通过',
  MATCHED: '已匹配',
  OPEN: '开放中',
  PENDING: '待审核',
  PENDING_REVIEW: '待审核',
  REJECTED: '已驳回',
  SUBMITTED: '待处理'
};

export function statusClass(status) {
  if (['APPROVED', 'OPEN', 'ACTIVE', 'ACCEPTED'].includes(status)) return 'success';
  if (['PENDING', 'PENDING_REVIEW', 'SUBMITTED'].includes(status)) return 'pending';
  if (status === 'REJECTED') return 'danger';
  return 'neutral';
}

export function statusLabel(status) {
  return statusText[status] || status || '未知状态';
}

export function workspacePath(user) {
  if (!user) return '/login';
  return {
    PARENT: '/parent',
    TUTOR: '/tutor',
    ADMIN: '/admin'
  }[user.role] || '/login';
}

export function formatCurrency(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0
  }).format(value ?? 0);
}

export function formatBudget(item) {
  return `${formatCurrency(item.budgetMin)} - ${formatCurrency(item.budgetMax)} / 小时`;
}

export function formatDate(value) {
  if (!value) return '暂无时间';
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
}

export function demandDraft() {
  return {
    title: '',
    subject: '数学',
    gradeLevel: '初中',
    location: '衡阳市蒸湘区',
    budgetMin: 120,
    budgetMax: 180,
    schedule: '周六下午',
    description: ''
  };
}

export function profileDraft() {
  return {
    school: '南华大学',
    major: '',
    subjects: '',
    introduction: '',
    teachingExperienceYears: 1,
    serviceMode: '线上',
    resumeText: ''
  };
}

export function toDemandPayload(form) {
  return {
    ...form,
    budgetMin: Number(form.budgetMin),
    budgetMax: Number(form.budgetMax)
  };
}
