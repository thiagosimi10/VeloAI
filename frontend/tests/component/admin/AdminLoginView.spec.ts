import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AdminLoginView from '@/views/admin/AdminLoginView.vue'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn() },
}))

import { http } from '@/services/http'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/admin/login', name: 'admin-login', component: AdminLoginView },
      { path: '/admin/tenants', name: 'admin-tenants', component: { template: '<div />' } },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(AdminLoginView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AdminLoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('renders the admin login form', async () => {
    const router = buildRouter()
    router.push('/admin/login')
    await router.isReady()

    const wrapper = mountView(router)

    expect(wrapper.text()).toContain('Painel Administrativo')
    expect(wrapper.find('#admin-email').exists()).toBe(true)
  })

  it('redirects to admin-tenants after a successful login', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: {
        data: {
          id: 'admin-1',
          email: 'operador@veloai.internal',
          first_name: 'Operador',
          last_name: null,
          must_change_password: false,
        },
      },
    })
    const router = buildRouter()
    router.push('/admin/login')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#admin-email').setValue('operador@veloai.internal')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/admin/auth/login', expect.any(Object))
    expect(router.currentRoute.value.name).toBe('admin-tenants')
  })

  it('shows an error message when login fails', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('network error'))
    const router = buildRouter()
    router.push('/admin/login')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#admin-email').setValue('operador@veloai.internal')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Não foi possível conectar')
  })
})
