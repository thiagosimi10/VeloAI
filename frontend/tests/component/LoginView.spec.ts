import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import LoginView from '@/views/LoginView.vue'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn() },
}))

import { http } from '@/services/http'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: LoginView },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
    ],
  })
}

function mountLoginView(router: ReturnType<typeof buildRouter>) {
  return mount(LoginView, {
    global: {
      plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]],
    },
  })
}

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('renders the login form', async () => {
    const router = buildRouter()
    router.push('/login')
    await router.isReady()

    const wrapper = mountLoginView(router)

    expect(wrapper.text()).toContain('Entrar no VeloAI')
    expect(wrapper.find('#email').exists()).toBe(true)
  })

  it('redirects to dashboard after a successful login', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { access_token: 'fake-token' } },
    })
    const router = buildRouter()
    router.push('/login')
    await router.isReady()

    const wrapper = mountLoginView(router)
    await wrapper.find('#email').setValue('user@empresa.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('shows an error message when login fails', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('network error'))
    const router = buildRouter()
    router.push('/login')
    await router.isReady()

    const wrapper = mountLoginView(router)
    await wrapper.find('#email').setValue('user@empresa.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Não foi possível conectar')
  })
})

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}
