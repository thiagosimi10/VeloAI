import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ProductStockView from '@/views/products/ProductStockView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

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

const RAW_MOVEMENT = {
  id: 'movement-1',
  product_id: 'product-1',
  movement: 'in' as const,
  quantity: 5,
  previous_stock: 10,
  current_stock: 15,
  reason: 'Compra de reposição',
  created_at: '2026-01-01T00:00:00Z',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/products', name: 'products', component: { template: '<div />' } },
      { path: '/products/:id/stock', name: 'products-stock', component: ProductStockView },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ProductStockView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders the product info and the movement history', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      if (url === '/api/v1/products/product-1/stock-movements') {
        return Promise.resolve({
          data: { data: [RAW_MOVEMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products/product-1/stock')
    await router.isReady()

    const wrapper = mount(ProductStockView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('SSD Kingston 1TB')
    expect(wrapper.text()).toContain('SSD-KGN-1TB')
    expect(wrapper.text()).toContain('Compra de reposição')
    expect(wrapper.text()).toContain('1 movimentação(ões)')
  })

  it('shows an empty state message when there is no history', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      if (url === '/api/v1/products/product-1/stock-movements') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products/product-1/stock')
    await router.isReady()

    const wrapper = mount(ProductStockView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhuma movimentação encontrada.')
  })

  it('registers a new movement and refreshes the product and history', async () => {
    let movementsCallCount = 0
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      if (url === '/api/v1/products/product-1/stock-movements') {
        movementsCallCount += 1
        return Promise.resolve({
          data: { data: [RAW_MOVEMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_MOVEMENT } })
    const router = buildRouter()
    router.push('/products/product-1/stock')
    await router.isReady()

    const wrapper = mount(ProductStockView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('#stock-movement-reason').setValue('Compra de reposição')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/products/product-1/stock-movements',
      expect.objectContaining({ movement: 'in', reason: 'Compra de reposição' }),
    )
    expect(movementsCallCount).toBe(2)
  })

  it('navigates back to the products list when "Voltar" is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      if (url === '/api/v1/products/product-1/stock-movements') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products/product-1/stock')
    await router.isReady()

    const wrapper = mount(ProductStockView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation(
      (url: string, config?: { params?: { page?: number } }) => {
        if (url === '/api/v1/products/product-1') {
          return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
        }
        if (url === '/api/v1/products/product-1/stock-movements') {
          const page = config?.params?.page ?? 1
          return Promise.resolve({
            data: {
              data: [RAW_MOVEMENT],
              meta: { page, page_size: 20, total: 25, pages: 2 },
            },
          }) as never
        }
        throw new Error(`unexpected GET ${url}`)
      },
    )
    const router = buildRouter()
    router.push('/products/product-1/stock')
    await router.isReady()

    const wrapper = mount(ProductStockView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/products/product-1/stock-movements',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/products/product-1/stock-movements',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
