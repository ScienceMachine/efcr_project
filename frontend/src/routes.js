import { createMemoryHistory, createRouter } from 'vue-router'

import SummaryPage from './components/SummaryPage.vue'
import AgencyDetailsPage from './components/AgencyDetailsPage.vue'

const routes = [
  { path: '', component: SummaryPage },
  { path: '/agency/:agencyName', component: AgencyDetailsPage, name: 'agency', props: true },
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

export default router
