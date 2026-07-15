import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ServiceOrderDetailView from '@/views/serviceOrders/ServiceOrderDetailView.vue'

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

const RAW_USER = {
  id: 'user-1',
  first_name: 'Carlos',
  last_name: 'Souza',
  email: 'carlos@empresa.test',
  active: true,
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

const RAW_SERVICE = {
  id: 'service-1',
  category_id: null,
  code: 'S000001',
  name: 'Formatação de Computador',
  description: null,
  estimated_time: 60,
  price: '180.00',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_ITEM = {
  id: 'item-1',
  service_order_id: 'order-1',
  product_id: 'product-1',
  service_id: null,
  quantity: 2,
  unit_price: '490.00',
  total: '980.00',
}

function buildRawOrder(overrides: Partial<{ status: string; items: unknown[] }> = {}) {
  return {
    id: 'order-1',
    number: 'OS-2026-000001',
    customer_id: 'customer-1',
    technician_id: null,
    status: overrides.status ?? 'open',
    equipment: 'Notebook Dell',
    serial_number: null,
    problem: 'Não liga',
    diagnosis: null,
    solution: null,
    total: '980.00',
    opened_at: '2026-01-01T00:00:00Z',
    finished_at: null,
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
    if (url === '/api/v1/users') {
      return Promise.resolve({
        data: { data: [RAW_USER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
      }) as never
    }
    if (url === '/api/v1/products') {
      return Promise.resolve({
        data: { data: [RAW_PRODUCT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
      }) as never
    }
    if (url === '/api/v1/services') {
      return Promise.resolve({
        data: { data: [RAW_SERVICE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
      }) as never
    }
    return Promise.resolve({ data: EMPTY_LIST }) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/service-orders', name: 'service-orders', component: { template: '<div />' } },
      {
        path: '/service-orders/:id',
        name: 'service-orders-detail',
        component: ServiceOrderDetailView,
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ServiceOrderDetailView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('renders the order info and items', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/service-orders/order-1') {
        return Promise.resolve({ data: { data: buildRawOrder() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    const router = buildRouter()
    router.push('/service-orders/order-1')
    await router.isReady()

    const wrapper = mount(ServiceOrderDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('OS-2026-000001')
    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.text()).toContain('SSD Kingston 1TB')
    expect(wrapper.find('[data-testid="start-order-button"]').exists()).toBe(true)
  })

  it('starts the order and updates the status shown', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/service-orders/order-1') {
        return Promise.resolve({ data: { data: buildRawOrder() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawOrder({ status: 'in_progress' }) },
    })
    const router = buildRouter()
    router.push('/service-orders/order-1')
    await router.isReady()

    const wrapper = mount(ServiceOrderDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="start-order-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/service-orders/order-1/start')
    expect(wrapper.text()).toContain('Em Atendimento')
  })

  it('closes the order when in progress', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/service-orders/order-1') {
        return Promise.resolve({ data: { data: buildRawOrder({ status: 'in_progress' }) } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawOrder({ status: 'completed' }) },
    })
    const router = buildRouter()
    router.push('/service-orders/order-1')
    await router.isReady()

    const wrapper = mount(ServiceOrderDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="close-order-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/service-orders/order-1/close',
      expect.objectContaining({}),
    )
    expect(wrapper.text()).toContain('Concluída')
  })

  it('cancels the order', async () => {
    mockCommonLookups()
    vi.mocked(http.get).mockImplementationOnce((url: string) => {
      if (url === '/api/v1/service-orders/order-1') {
        return Promise.resolve({ data: { data: buildRawOrder() } }) as never
      }
      throw new Error(`unexpected first GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: buildRawOrder({ status: 'cancelled' }) },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/service-orders/order-1')
    await router.isReady()

    const wrapper = mount(ServiceOrderDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="cancel-order-button"]').trigger('click')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/service-orders/order-1/cancel')
    expect(wrapper.text()).toContain('Cancelada')
  })

  it('removes an item after confirmation', async () => {
    let orderCallCount = 0
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/service-orders/order-1') {
        orderCallCount += 1
        const items = orderCallCount === 1 ? [RAW_ITEM] : []
        return Promise.resolve({ data: { data: buildRawOrder({ items } as never) } }) as never
      }
      if (url === '/api/v1/customers') {
        return Promise.resolve({
          data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
        }) as never
      }
      if (url === '/api/v1/users') {
        return Promise.resolve({
          data: { data: [RAW_USER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
        }) as never
      }
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [RAW_PRODUCT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      if (url === '/api/v1/services') {
        return Promise.resolve({
          data: { data: [RAW_SERVICE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      return Promise.resolve({ data: EMPTY_LIST }) as never
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/service-orders/order-1')
    await router.isReady()

    const wrapper = mount(ServiceOrderDetailView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[aria-label="Remover item"]').trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/service-orders/order-1/items/item-1')
  })
})
