import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import SaleFormView from '@/views/sales/SaleFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_CUSTOMERS_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}

const RAW_SALE = {
  id: 'sale-1',
  customer_id: '',
  status: 'open' as const,
  payment_method: null,
  discount: '0.00',
  total: '0.00',
  created_at: '2026-01-01T00:00:00Z',
  items: [],
}

function mockLookupFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/sales', name: 'sales', component: { template: '<div />' } },
      { path: '/sales/new', name: 'sales-new', component: SaleFormView },
      { path: '/sales/:id', name: 'sales-detail', component: { template: '<div />' } },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('SaleFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders an empty create form', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/sales/new')
    await router.isReady()

    const wrapper = mount(SaleFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nova Venda')
  })

  it('creates a sale and redirects to the detail page on success', async () => {
    mockLookupFetches()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SALE } })
    const router = buildRouter()
    router.push('/sales/new')
    await router.isReady()

    const wrapper = mount(SaleFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/sales',
      expect.objectContaining({ payment_method: null }),
    )
    expect(router.currentRoute.value.name).toBe('sales-detail')
    expect(router.currentRoute.value.params.id).toBe('sale-1')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/sales/new')
    await router.isReady()

    const wrapper = mount(SaleFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('sales')
  })
})
