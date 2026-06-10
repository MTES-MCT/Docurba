import { createRouter, createWebHistory } from 'vue-router'
import { routes, handleHotUpdate } from 'vue-router/auto-routes'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from) => {
  const { initialize, initialized, signedIn } = useAuth()

  if (!initialized.value) {
    await initialize()
  }
  // Signed in only guard
  if (to.meta.signedInOnly) {
    return signedIn.value || (from ?? '/')
  }
  // Signed out only guard
  if (to.meta.signedOutOnly) {
    return !signedIn.value || (from ?? '/')
  }
})

export default router

if (import.meta.hot) {
  handleHotUpdate(router)
}
