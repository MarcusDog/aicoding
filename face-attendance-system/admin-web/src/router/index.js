import { createRouter, createWebHistory } from "vue-router";

import AttendanceList from "../views/AttendanceList.vue";
import Dashboard from "../views/Dashboard.vue";
import FaceManage from "../views/FaceManage.vue";
import Login from "../views/Login.vue";
import OperationLogs from "../views/OperationLogs.vue";
import Reports from "../views/Reports.vue";
import RuleSettings from "../views/RuleSettings.vue";
import UserManage from "../views/UserManage.vue";

const routes = [
  { path: "/login", component: Login, meta: { public: true } },
  { path: "/", component: Dashboard },
  { path: "/users", component: UserManage },
  { path: "/attendance", component: AttendanceList },
  { path: "/faces", component: FaceManage },
  { path: "/rules", component: RuleSettings },
  { path: "/reports", component: Reports },
  { path: "/logs", component: OperationLogs },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem("attendance_admin_token");
  if (!to.meta.public && !token) {
    return "/login";
  }
  if (to.path === "/login" && token) {
    return "/";
  }
  return true;
});

export default router;
