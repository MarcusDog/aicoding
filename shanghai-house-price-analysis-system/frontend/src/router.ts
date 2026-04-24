import { createRouter, createWebHistory } from 'vue-router'

import CommunitiesPage from './pages/CommunitiesPage.vue'
import ListingsPage from './pages/ListingsPage.vue'
import OverviewPage from './pages/OverviewPage.vue'
import PredictionsPage from './pages/PredictionsPage.vue'
import TrendsPage from './pages/TrendsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/overview' },
    { path: '/overview', name: 'overview', component: OverviewPage },
    { path: '/listings', name: 'listings', component: ListingsPage },
    { path: '/communities', name: 'communities', component: CommunitiesPage },
    { path: '/trends', name: 'trends', component: TrendsPage },
    { path: '/predictions', name: 'predictions', component: PredictionsPage },
  ],
})

export default router
