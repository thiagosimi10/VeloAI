import { AxiosError, AxiosHeaders } from 'axios'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ProductFormView from '@/views/products/ProductFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_LIST_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
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

function mockLookupFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/categories' || url === '/api/v1/suppliers') {
      return Promise.resolve(EMPTY_LIST_RESPONSE) as never
    }
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/products', name: 'products', component: { template: '<div />' } },
      { path: '/products/new', name: 'products-new', component: ProductFormView },
      { path: '/products/:id/edit', name: 'products-edit', component: ProductFormView },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(ProductFormView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ProductFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('renders an empty create form', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/products/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    expect(wrapper.text()).toContain('Novo Produto')
    expect((wrapper.find('#product-sku').element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('#product-sku').element as HTMLInputElement).disabled).toBe(false)
  })

  it('creates a product and redirects to the list on success', async () => {
    mockLookupFetches()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_PRODUCT } })
    const router = buildRouter()
    router.push('/products/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('#product-sku').setValue('SSD-KGN-1TB')
    await wrapper.find('#product-name').setValue('SSD Kingston 1TB')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/products',
      expect.objectContaining({ sku: 'SSD-KGN-1TB', name: 'SSD Kingston 1TB' }),
    )
    expect(router.currentRoute.value.name).toBe('products')
  })

  it('shows an error message and stays on the page when creation fails', async () => {
    mockLookupFetches()
    const error = new AxiosError('Conflict', '409', undefined, undefined, {
      status: 409,
      statusText: 'Conflict',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { message: 'SKU já cadastrado.' },
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const router = buildRouter()
    router.push('/products/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('#product-sku').setValue('SSD-KGN-1TB')
    await wrapper.find('#product-name').setValue('SSD Kingston 1TB')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('SKU já cadastrado.')
    expect(router.currentRoute.value.name).toBe('products-new')
  })

  it('loads existing product data in edit mode and disables the SKU field', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories' || url === '/api/v1/suppliers') {
        return Promise.resolve(EMPTY_LIST_RESPONSE) as never
      }
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      return Promise.reject(new Error(`unexpected GET ${url}`)) as never
    })
    const router = buildRouter()
    router.push('/products/product-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Editar Produto')
    expect((wrapper.find('#product-sku').element as HTMLInputElement).value).toBe('SSD-KGN-1TB')
    expect((wrapper.find('#product-sku').element as HTMLInputElement).disabled).toBe(true)
  })

  it('updates a product and redirects to the list on success', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories' || url === '/api/v1/suppliers') {
        return Promise.resolve(EMPTY_LIST_RESPONSE) as never
      }
      if (url === '/api/v1/products/product-1') {
        return Promise.resolve({ data: { data: RAW_PRODUCT } }) as never
      }
      return Promise.reject(new Error(`unexpected GET ${url}`)) as never
    })
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_PRODUCT, name: 'SSD Kingston 1TB NVMe' } },
    })
    const router = buildRouter()
    router.push('/products/product-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('#product-name').setValue('SSD Kingston 1TB NVMe')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/products/product-1',
      expect.objectContaining({ name: 'SSD Kingston 1TB NVMe' }),
    )
    expect(router.currentRoute.value.name).toBe('products')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/products/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('products')
  })
})
