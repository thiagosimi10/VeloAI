import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AccountPayableDetailView from '@/views/finance/AccountPayableDetailView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_SUPPLIER = {
  id: 'supplier-1',
  code: 'F000001',
  type: 'PJ' as const,
  name: 'Tech Distribuidora LTDA',
  document: '12345678000199',
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

function buildRawPayable(overrides: Partial<{ status: string; payment_date: string | null }> = {}) {
  return {
    id: 'payable-1',
    supplier_id: 'supplier-1',
    due_date: '2026-08-01',
    amount: '320.00',
    status: overrides.status ?? 'pending',
    payment_date: overrides.payment_date ?? null,
    is_overdue: false,
  }
}

function mockCommonLookups(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/suppliers') {
      return Promise.resolve({
        data: { data: [RAW_SUPPLIER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
      }) as never
    }
    return Promise.resolve({ data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } } }) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accounts-payable', name: 'accounts-payable', component: { template: '<div />' } },
      {
        path: '/accounts-payable/:id',
        name: 'accounts-payable-detail',
        component: AccountPayableDetailView,
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AccountPayableDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders the payable info', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-payable/payable-1') {
        return Promise.resolve({ data: { data: buildRawPayable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-payable/payable-1')
    await router.isReady()

    const wrapper = mount(AccountPayableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Tech Distribuidora LTDA')
    expect(wrapper.find('[data-testid="pay-button"]').exists()).toBe(true)
  })

  it('pays the payable and updates the status shown', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-payable/payable-1') {
        return Promise.resolve({ data: { data: buildRawPayable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawPayable({ status: 'paid', payment_date: '2026-07-20' }) },
    })
    const router = buildRouter()
    router.push('/accounts-payable/payable-1')
    await router.isReady()

    const wrapper = mount(AccountPayableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="pay-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-payable/payable-1/pay')
    expect(wrapper.text()).toContain('Paga')
  })

  it('cancels the payable', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/accounts-payable/payable-1') {
        return Promise.resolve({ data: { data: buildRawPayable() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawPayable({ status: 'cancelled' }) },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/accounts-payable/payable-1')
    await router.isReady()

    const wrapper = mount(AccountPayableDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="cancel-payable-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-payable/payable-1/cancel')
    expect(wrapper.text()).toContain('Cancelada')
  })
})
