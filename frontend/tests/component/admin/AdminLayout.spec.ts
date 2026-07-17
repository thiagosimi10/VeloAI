import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAdminAuthStore } from '@/stores/adminAuth'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/admin/tenants', name: 'admin-tenants', component: { template: '<div />' } },
      { path: '/admin/login', name: 'admin-login', component: { template: '<div />' } },
    ],
  })
}

describe('AdminLayout', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('renders the admin email and the slot content', async () => {
    const router = buildRouter()
    await router.push('/admin/tenants')
    const adminAuthStore = useAdminAuthStore()
    adminAuthStore.$patch({
      admin: {
        id: 'admin-1',
        email: 'operador@veloai.internal',
        firstName: 'Operador',
        lastName: null,
        mustChangePassword: false,
      },
    })

    const wrapper = mount(AdminLayout, {
      global: { plugins: [router] },
      slots: { default: '<p>Conteúdo da página</p>' },
    })

    expect(wrapper.text()).toContain('operador@veloai.internal')
    expect(wrapper.text()).toContain('Conteúdo da página')
  })

  it('logs out and redirects to admin-login when "Sair" is clicked', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: {} } })
    const router = buildRouter()
    await router.push('/admin/tenants')
    const adminAuthStore = useAdminAuthStore()
    adminAuthStore.$patch({
      admin: {
        id: 'admin-1',
        email: 'operador@veloai.internal',
        firstName: 'Operador',
        lastName: null,
        mustChangePassword: false,
      },
    })

    const wrapper = mount(AdminLayout, { global: { plugins: [router] } })

    await wrapper.find('[data-testid="admin-logout-button"]').trigger('click')
    await flushPromises()

    expect(adminAuthStore.isAuthenticated).toBe(false)
    expect(router.currentRoute.value.name).toBe('admin-login')
  })
})

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}
