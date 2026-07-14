import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import DashboardView from '@/views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: LoginView, meta: { layout: 'auth' } },
      {
        path: '/dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { layout: 'default' },
      },
    ],
  })
}

describe('App', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('uses AuthLayout (no sidebar) for routes marked as "auth"', async () => {
    const router = buildRouter()
    await router.push('/login')

    const wrapper = mount(App, { global: { plugins: [router, PrimeVue] } })

    expect(wrapper.find('[data-testid="app-sidebar"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Entrar no VeloAI')
  })

  it('uses DefaultLayout (with sidebar) for routes marked as "default"', async () => {
    const router = buildRouter()
    await router.push('/dashboard')

    const wrapper = mount(App, { global: { plugins: [router, PrimeVue] } })

    expect(wrapper.find('[data-testid="app-sidebar"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Bem-vindo ao VeloAI')
  })
})
