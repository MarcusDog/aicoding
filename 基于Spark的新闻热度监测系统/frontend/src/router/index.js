import { createRouter, createWebHistory } from "vue-router";
import DashboardPage from "../pages/DashboardPage.vue";
import NewsSearchPage from "../pages/NewsSearchPage.vue";
import EventAnalysisPage from "../pages/EventAnalysisPage.vue";
import ServiceCenterPage from "../pages/ServiceCenterPage.vue";
import InfluenceBoardPage from "../pages/InfluenceBoardPage.vue";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/dashboard", component: DashboardPage },
  { path: "/news", component: NewsSearchPage },
  { path: "/events", component: EventAnalysisPage },
  { path: "/influence", component: InfluenceBoardPage },
  { path: "/services", component: ServiceCenterPage },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
