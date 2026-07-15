import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ProductsListView from '@/views/products/ProductsListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CATEGORY = {
  id: 'category-1',
  name: 'Armazenamento',
  description: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_PRODUCT_1 = {
  id: 'product-1',
  category_id: 'category-1',
  supplier_id: null,
  sku: 'SSD-KGN-1TB',
  barcode: null,
  name: 'SSD Kingston 1TB',
  description: null,
  cost_price: '320.00',
  sale_price: '490.00',
  stock: 20,
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

const RAW_PRODUCT_2 = { ...RAW_PRODUCT_1, id: 'product-2', sku: 'HD-SEAGATE-2TB', name: 'HD Seagate 2TB' }

const EMPTY_CATEGORY_RESPONSE = {
  data: { data: [RAW_CATEGORY], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/products', name: 'products', component: ProductsListView },
      { path: '/products/new', name: 'products-new', component: { template: '<div />' } },
      { path: '/products/:id/edit', name: 'products-edit', component: { template: '<div />' } },
      { path: '/products/:id/stock', name: 'products-stock', component: { template: '<div />' } },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ProductsListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the products returned by the store with the resolved category name', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: {
            data: [RAW_PRODUCT_1, RAW_PRODUCT_2],
            meta: { page: 1, page_size: 20, total: 2, pages: 1 },
          },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('SSD Kingston 1TB')
    expect(wrapper.text()).toContain('HD Seagate 2TB')
    expect(wrapper.text()).toContain('Armazenamento')
    expect(wrapper.text()).toContain('2 produto(s)')
  })

  it('shows an empty state message when there are no products', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum produto encontrado.')
  })

  it('navigates to the new-product route when the button is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-product-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products-new')
  })

  it('deletes a product after confirmation and refreshes the list', async () => {
    let productsCallCount = 0
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        productsCallCount += 1
        if (productsCallCount === 1) {
          return Promise.resolve({
            data: {
              data: [RAW_PRODUCT_1],
              meta: { page: 1, page_size: 20, total: 1, pages: 1 },
            },
          }) as never
        }
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_PRODUCT_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/products/product-1')
    expect(productsCallCount).toBe(2)
  })

  it('navigates to the edit route when the edit icon is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [RAW_PRODUCT_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Editar ${RAW_PRODUCT_1.name}"]`).trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products-edit')
    expect(router.currentRoute.value.params.id).toBe('product-1')
  })

  it('navigates to the stock history route when the history icon is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/products') {
        return Promise.resolve({
          data: { data: [RAW_PRODUCT_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Estoque de ${RAW_PRODUCT_1.name}"]`).trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products-stock')
    expect(router.currentRoute.value.params.id).toBe('product-1')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation(
      (url: string, config?: { params?: { page?: number } }) => {
        if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
        if (url === '/api/v1/products') {
          const page = config?.params?.page ?? 1
          return Promise.resolve({
            data: { data: [RAW_PRODUCT_1], meta: { page, page_size: 20, total: 25, pages: 2 } },
          }) as never
        }
        throw new Error(`unexpected GET ${url}`)
      },
    )
    const router = buildRouter()
    router.push('/products')
    await router.isReady()

    const wrapper = mount(ProductsListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/products',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/products',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
