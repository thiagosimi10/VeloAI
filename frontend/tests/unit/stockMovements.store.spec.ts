import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useStockMovementsStore } from '@/stores/stockMovements'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
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

describe('stock movements store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('fetches and maps movements for a product', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_MOVEMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useStockMovementsStore()

    await store.fetchMovements('product-1')

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/products/product-1/stock-movements',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.currentStock).toBe(15)
    expect(store.error).toBeNull()
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useStockMovementsStore()

    await store.fetchMovements('product-1')

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createMovement posts the payload and returns the mapped movement', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_MOVEMENT } })
    const store = useStockMovementsStore()

    const created = await store.createMovement('product-1', {
      movement: 'in',
      quantity: 5,
      reason: 'Compra de reposição',
    })

    expect(created?.currentStock).toBe(15)
    expect(http.post).toHaveBeenCalledWith('/api/v1/products/product-1/stock-movements', {
      movement: 'in',
      quantity: 5,
      reason: 'Compra de reposição',
    })
  })

  it('createMovement returns null and sets error when stock is insufficient', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(
      buildConflictError('Estoque insuficiente para esta movimentação.'),
    )
    const store = useStockMovementsStore()

    const created = await store.createMovement('product-1', {
      movement: 'out',
      quantity: 999,
      reason: 'Venda balcão',
    })

    expect(created).toBeNull()
    expect(store.error).toBe('Estoque insuficiente para esta movimentação.')
  })

  it('setPage updates the page used by the next fetch', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 2, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useStockMovementsStore()
    store.setPage(2)

    await store.fetchMovements('product-1')

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/products/product-1/stock-movements',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )
  })
})
