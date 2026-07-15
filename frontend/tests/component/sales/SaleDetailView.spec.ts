import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import SaleDetailView from '@/views/sales/SaleDetailView.vue'

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

const RAW_PRODUCT = {
  id: 'product-1',
  category_id: null,
  supplier_id: null,
  sku: 'SSD-KGN-1TB',
  barcode: null,
  name: 'SSD Kingston 1TB',
  description: null,
  cost_price: '320.00',
  sale_price: '490.00',
  stock: 15,
  minimum_stock: null,
  maximum_stock: null,
  unit: 'UN',
  weight: null,
  active: true,
  margin: '170.00',
  margin_percentage: '53.12',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_ITEM = {
  id: 'item-1',
  sale_id: 'sale-1',
  product_id: 'product-1',
  quantity: 2,
  unit_price: '490.00',
  total: '980.00',
}

function buildRawSale(overrides: Partial<{ status: string; items: unknown[] }> = {}) {
  return {
    id: 'sale-1',
    customer_id: 'customer-1',
    status: overrides.status ?? 'open',
    payment_method: 'pix',
    discount: '0.00',
    total: '980.00',
    created_at: '2026-01-01T00:00:00Z',
    items: overrides.items ?? [RAW_ITEM],
  }
}

const EMPTY_LIST = { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } }

function mockCommonLookups(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/customers') {
      return Promise.resolve({
        data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
      }) as never
    }
    if (url === '/api/v1/products') {
      return Promise.resolve({
        data: { data: [RAW_PRODUCT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
      }) as never
    }
    return Promise.resolve({ data: EMPTY_LIST }) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/sales', name: 'sales', component: { template: '<div />' } },
      { path: '/sales/:id', name: 'sales-detail', component: SaleDetailView },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('SaleDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('renders the sale info and items', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/sales/sale-1') {
        return Promise.resolve({ data: { data: buildRawSale() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    const router = buildRouter()
    router.push('/sales/sale-1')
    await router.isReady()

    const wrapper = mount(SaleDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.text()).toContain('SSD Kingston 1TB')
    expect(wrapper.find('[data-testid="complete-sale-button"]').exists()).toBe(true)
  })

  it('completes the sale and updates the status shown', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/sales/sale-1') {
        return Promise.resolve({ data: { data: buildRawSale() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawSale({ status: 'paid' }) },
    })
    const router = buildRouter()
    router.push('/sales/sale-1')
    await router.isReady()

    const wrapper = mount(SaleDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="complete-sale-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/sales/sale-1/complete')
    expect(wrapper.text()).toContain('Paga')
  })

  it('cancels the sale', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/sales/sale-1') {
        return Promise.resolve({ data: { data: buildRawSale() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawSale({ status: 'cancelled' }) },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/sales/sale-1')
    await router.isReady()

    const wrapper = mount(SaleDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="cancel-sale-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/sales/sale-1/cancel')
    expect(wrapper.text()).toContain('Cancelada')
  })

  it('removes an item after confirmation', async () => {
    let saleCallCount = 0
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/sales/sale-1') {
        saleCallCount += 1
        const items = saleCallCount === 1 ? [RAW_ITEM] : []
        return Promise.resolve({ data: { data: buildRawSale({ items } as never) } }) as never
      }
      if (url === '/api/v1/customers') {
        return Promise.resolve({
          data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
        }) as never
      }
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [RAW_PRODUCT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      return Promise.resolve({ data: EMPTY_LIST }) as never
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/sales/sale-1')
    await router.isReady()

    const wrapper = mount(SaleDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[aria-label="Remover item"]').trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/sales/sale-1/items/item-1')
  })
})
