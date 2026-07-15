import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AccountReceivableDetailView from '@/views/finance/AccountReceivableDetailView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CUSTOMER = {
  id: 'customer-1',
  code: 'C000001',
  type: 'PF' as const,
  name: 'João Silva',
  document: '12345678901',
  state_registration: null,
  municipal_registration: null,
  email: null,
  phone: null,
  mobile: null,
  whatsapp: null,
  zipcode: null,
  street: null,
  number: null,
  district: null,
  city: null,
  state: null,
  country: 'Brasil',
  notes: null,
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function buildRawReceivable(overrides: Partial<{ status: string; payment_date: string | null }> = {}) {
  return {
    id: 'receivable-1',
    customer_id: 'customer-1',
    due_date: '2026-08-01',
    amount: '980.00',
    status: overrides.status ?? 'pending',
    payment_date: overrides.payment_date ?? null,
    is_overdue: false,
  }
}

function mockCommonLookups(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/customers') {
      return Promise.resolve({
        data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
      }) as never
    }
    return Promise.resolve({ data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } } }) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accounts-receivable', name: 'accounts-receivable', component: { template: '<div />' } },
      {
        path: '/accounts-receivable/:id',
        name: 'accounts-receivable-detail',
        component: AccountReceivableDetailView,
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AccountReceivableDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders the receivable info', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-receivable/receivable-1') {
        return Promise.resolve({ data: { data: buildRawReceivable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-receivable/receivable-1')
    await router.isReady()

    const wrapper = mount(AccountReceivableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.find('[data-testid="receive-button"]').exists()).toBe(true)
  })

  it('receives the receivable and updates the status shown', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-receivable/receivable-1') {
        return Promise.resolve({ data: { data: buildRawReceivable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawReceivable({ status: 'received', payment_date: '2026-07-20' }) },
    })
    const router = buildRouter()
    router.push('/accounts-receivable/receivable-1')
    await router.isReady()

    const wrapper = mount(AccountReceivableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="receive-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-receivable/receivable-1/receive')
    expect(wrapper.text()).toContain('Recebida')
  })

  it('cancels the receivable', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-receivable/receivable-1') {
        return Promise.resolve({ data: { data: buildRawReceivable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawReceivable({ status: 'cancelled' }) },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/accounts-receivable/receivable-1')
    await router.isReady()

    const wrapper = mount(AccountReceivableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="cancel-receivable-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-receivable/receivable-1/cancel')
    expect(wrapper.text()).toContain('Cancelada')
  })
})
