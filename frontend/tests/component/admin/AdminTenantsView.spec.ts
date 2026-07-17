import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AdminTenantsView from '@/views/admin/AdminTenantsView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_SUMMARY = {
  total_tenants: 1,
  trial_count: 0,
  active_count: 1,
  pending_payment_count: 0,
  overdue_count: 0,
  suspended_count: 0,
  canceled_count: 0,
  expired_count: 0,
  estimated_mrr: '129.90',
}

const RAW_TENANT = {
  tenant_id: 'tenant-1',
  legal_name: 'Assistência Silva',
  document: '12345678000199',
  status: 'ACTIVE',
  plan_name: 'VeloAI Professional',
  subscription_status: 'ACTIVE',
  trial_ends_at: null,
}

function mockAllFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/admin/summary') {
      return Promise.resolve({ data: { data: RAW_SUMMARY } }) as never
    }
    if (url === '/api/v1/admin/tenants') {
      return Promise.resolve({ data: { data: [RAW_TENANT] } }) as never
    }
    throw new Error(`unexpected GET ${url}`)
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/admin/tenants', name: 'admin-tenants', component: AdminTenantsView },
      {
        path: '/admin/tenants/:id/audit-log',
        name: 'admin-tenant-audit-log',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AdminTenantsView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('renders the summary cards and the tenants table', async () => {
    mockAllFetches()
    const router = buildRouter()
    router.push('/admin/tenants')
    await router.isReady()

    const wrapper = mount(AdminTenantsView, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Assistência Silva')
    expect(wrapper.text()).toContain('VeloAI Professional')
    expect(wrapper.text()).toContain('R$')
  })

  it('navigates to the audit log when a tenant row link is clicked', async () => {
    mockAllFetches()
    const router = buildRouter()
    router.push('/admin/tenants')
    await router.isReady()

    const wrapper = mount(AdminTenantsView, { global: { plugins: [router] } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('[data-testid="audit-log-link-tenant-1"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('admin-tenant-audit-log')
    expect(router.currentRoute.value.params.id).toBe('tenant-1')
  })
})
