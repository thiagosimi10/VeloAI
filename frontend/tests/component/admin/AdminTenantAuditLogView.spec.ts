import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AdminTenantAuditLogView from '@/views/admin/AdminTenantAuditLogView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_ENTRY = {
  id: 'log-1',
  action: 'SUBSCRIPTION_CANCELED',
  resource: 'subscriptions',
  before: { status: 'ACTIVE' },
  after: { status: 'CANCELED' },
  created_at: '2026-07-16T10:00:00Z',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/admin/tenants/:id/audit-log',
        name: 'admin-tenant-audit-log',
        component: AdminTenantAuditLogView,
      },
      { path: '/admin/tenants', name: 'admin-tenants', component: { template: '<div />' } },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AdminTenantAuditLogView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('renders the audit log entries for the tenant in the route', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_ENTRY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const router = buildRouter()
    router.push('/admin/tenants/tenant-1/audit-log')
    await router.isReady()

    const wrapper = mount(AdminTenantAuditLogView, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(http.get).toHaveBeenCalledWith('/api/v1/admin/tenants/tenant-1/audit-log', {
      params: { page: 1 },
    })
    expect(wrapper.text()).toContain('SUBSCRIPTION_CANCELED')
  })

  it('shows an empty state message when there are no audit log entries', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/admin/tenants/tenant-1/audit-log')
    await router.isReady()

    const wrapper = mount(AdminTenantAuditLogView, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum evento registrado.')
  })

  it('navigates back to admin-tenants when the back button is clicked', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/admin/tenants/tenant-1/audit-log')
    await router.isReady()

    const wrapper = mount(AdminTenantAuditLogView, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('admin-tenants')
  })
})
