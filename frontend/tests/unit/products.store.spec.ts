import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useProductsStore } from '@/stores/products'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_PRODUCT = {
  id: 'product-1',
  category_id: 'category-1',
  supplier_id: 'supplier-1',
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

describe('products store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps products, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_PRODUCT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useProductsStore()

    await store.fetchProducts()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.costPrice).toBe(320)
    expect(store.items[0]?.salePrice).toBe(490)
    expect(store.items[0]?.margin).toBe(170)
    expect(store.items[0]?.marginPercentage).toBe(53.12)
    expect(store.error).toBeNull()
  })

  it('sends the category filter as category_id', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useProductsStore()
    store.setCategoryFilter('category-1')

    await store.fetchProducts()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/products',
      expect.objectContaining({ params: expect.objectContaining({ category_id: 'category-1' }) }),
    )
  })

  it('setSearch and setCategoryFilter reset the page back to 1', () => {
    const store = useProductsStore()
    store.setPage(3)
    store.setSearch('ssd')
    expect(store.page).toBe(1)

    store.setPage(4)
    store.setCategoryFilter('category-1')
    expect(store.page).toBe(1)
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useProductsStore()

    await store.fetchProducts()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createProduct posts the snake_case payload and returns the mapped product', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_PRODUCT } })
    const store = useProductsStore()

    const created = await store.createProduct({
      sku: 'SSD-KGN-1TB',
      name: 'SSD Kingston 1TB',
      costPrice: 320,
      salePrice: 490,
    })

    expect(created?.sku).toBe('SSD-KGN-1TB')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/products',
      expect.objectContaining({ sku: 'SSD-KGN-1TB', cost_price: 320, sale_price: 490 }),
    )
  })

  it('createProduct returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(buildConflictError('SKU já cadastrado.'))
    const store = useProductsStore()

    const created = await store.createProduct({
      sku: 'SSD-KGN-1TB',
      name: 'SSD Kingston 1TB',
      costPrice: 320,
      salePrice: 490,
    })

    expect(created).toBeNull()
    expect(store.error).toBe('SKU já cadastrado.')
  })

  it('updateProduct patches the given id', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: RAW_PRODUCT } })
    const store = useProductsStore()

    const updated = await store.updateProduct('product-1', {
      name: 'SSD Kingston 1TB',
      costPrice: 320,
      salePrice: 550,
    })

    expect(updated).not.toBeNull()
    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/products/product-1',
      expect.objectContaining({ sale_price: 550 }),
    )
  })

  it('deleteProduct returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useProductsStore()

    const success = await store.deleteProduct('product-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/products/product-1')
  })

  it('getProduct returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useProductsStore()

    const product = await store.getProduct('missing-id')

    expect(product).toBeNull()
  })
})
