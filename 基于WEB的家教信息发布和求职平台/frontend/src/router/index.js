import { createRouter, createWebHistory } from 'vue-router'
import { getCurrentUser } from '../stores/session'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import DemandDetailView from '../views/DemandDetailView.vue'
import DemandListView from '../views/DemandListView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ParentDashboardView from '../views/ParentDashboardView.vue'
import RegisterView from '../views/RegisterView.vue'
import TutorDashboardView from '../views/TutorDashboardView.vue'
import TutorDetailView from '../views/TutorDetailView.vue'
import TutorListView from '../views/TutorListView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView, meta: { title: '首页' } },
  { path: '/login', name: 'login', component: LoginView, meta: { title: '登录' } },
  { path: '/register', name: 'register', component: RegisterView, meta: { title: '注册' } },
  { path: '/demands', name: 'demands', component: DemandListView, meta: { title: '家教需求' } },
  { path: '/demands/:id', name: 'demand-detail', component: DemandDetailView, meta: { title: '需求详情' } },
  { path: '/tutors', name: 'tutors', component: TutorListView, meta: { title: '教员信息' } },
  { path: '/tutors/:id', name: 'tutor-detail', component: TutorDetailView, meta: { title: '教员详情' } },
  { path: '/tutor-users/:userId/profile', name: 'tutor-user-profile', component: TutorDetailView, meta: { title: '教员资料详情' } },
  { path: '/parent', name: 'parent-dashboard', component: ParentDashboardView, meta: { title: '家长工作台', role: 'PARENT' } },
  { path: '/tutor', name: 'tutor-dashboard', component: TutorDashboardView, meta: { title: '教员工作台', role: 'TUTOR' } },
  { path: '/admin', name: 'admin-dashboard', component: AdminDashboardView, meta: { title: '管理后台', role: 'ADMIN' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const requiredRole = to.meta.role
  if (!requiredRole) {
    return true
  }

  const user = getCurrentUser()
  if (!user) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (user.role !== requiredRole) {
    return { name: `${user.role.toLowerCase()}-dashboard` }
  }

  return true
})

router.afterEach((to) => {
  document.title = `南华家教平台 - ${to.meta.title || '首页'}`
})

export default router
