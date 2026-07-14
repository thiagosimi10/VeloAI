import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useAuthStore } from '@/stores/auth'

describe('router', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('redirects to /login when navigating to a protected route while unauthenticated', async () => {
    const router = (await import('@/router')).default
    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/dashboard')
  })

  it('allows navigating to /dashboard when authenticated', async () => {
    const authStore = useAuthStore()
    authStore.$patch({ accessToken: 'fake-token' })

    const router = (await import('@/router')).default
    await router.push('/dashboard')

    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('renders the not-found view for unknown paths', async () => {
    const router = (await import('@/router')).default
    await router.push('/rota-que-nao-existe')

    expect(router.currentRoute.value.name).toBe('not-found')
  })
})
