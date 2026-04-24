import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginView from '../views/auth/LoginView.vue';
import StudentLayout from '../layouts/StudentLayout.vue';
import AdminLayout from '../layouts/AdminLayout.vue';
import StudentHomeView from '../views/student/StudentHomeView.vue';
import ActivityListView from '../views/student/ActivityListView.vue';
import ActivityDetailView from '../views/student/ActivityDetailView.vue';
import MySignupView from '../views/student/MySignupView.vue';
import CheckinView from '../views/student/CheckinView.vue';
import MyHoursView from '../views/student/MyHoursView.vue';
import MyMessagesView from '../views/student/MyMessagesView.vue';
import ProfileView from '../views/student/ProfileView.vue';
import AdminDashboardView from '../views/admin/AdminDashboardView.vue';
import StudentManageView from '../views/admin/StudentManageView.vue';
import ActivityManageView from '../views/admin/ActivityManageView.vue';
import SignupReviewView from '../views/admin/SignupReviewView.vue';
import SignManageView from '../views/admin/SignManageView.vue';
import HoursManageView from '../views/admin/HoursManageView.vue';
import NoticeManageView from '../views/admin/NoticeManageView.vue';
import ReportView from '../views/admin/ReportView.vue';
import AdminManageView from '../views/admin/AdminManageView.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  {
    path: '/student',
    component: StudentLayout,
    meta: { role: 'STUDENT' },
    children: [
      { path: '', redirect: '/student/home' },
      { path: 'home', component: StudentHomeView },
      { path: 'activities', component: ActivityListView },
      { path: 'activities/:id', component: ActivityDetailView },
      { path: 'signups', component: MySignupView },
      { path: 'checkin', component: CheckinView },
      { path: 'hours', component: MyHoursView },
      { path: 'messages', component: MyMessagesView },
      { path: 'profile', component: ProfileView }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { role: 'ADMIN' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', component: AdminDashboardView },
      { path: 'students', component: StudentManageView },
      { path: 'activities', component: ActivityManageView },
      { path: 'signups', component: SignupReviewView },
      { path: 'signs', component: SignManageView },
      { path: 'hours', component: HoursManageView },
      { path: 'notices', component: NoticeManageView },
      { path: 'reports', component: ReportView },
      { path: 'admins', component: AdminManageView }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  if (authStore.token && !authStore.user) {
    await authStore.restore();
  }
  if (to.path === '/login') {
    return true;
  }
  if (!authStore.token || !authStore.user) {
    return '/login';
  }
  if (to.meta.role && authStore.user.roleCode !== to.meta.role) {
    return authStore.user.roleCode === 'ADMIN' ? '/admin/dashboard' : '/student/home';
  }
  return true;
});

export default router;
