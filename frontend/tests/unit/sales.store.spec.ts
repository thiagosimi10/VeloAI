import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useSalesStore } from '@/stores/sales'

function buildError(status: number, message: string): AxiosError {
  return new AxiosError('Error', String(status), undefined, undefined, {
    status,
    statusText: 'Error',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_SALE = {
  id: 'sale-1',
  customer_id: 'customer-1',
  status: 'open' as const,
  payment_method: 'pix',
  discount: '0.00',
  total: '0.00',
  created_at: '2026-01-01T00:00:00Z',
  items: [],
}

const RAW_ITEM = {
  id: 'item-1',
  sale_id: 'sale-1',
  product_id: 'product-1',
  quantity: 2,
  unit_price: '490.00',
  total: '980.00',
}

describe('sales store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps sales, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_SALE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useSalesStore()

    await store.fetchSales()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.total).toBe(0)
    expect(store.items[0]?.paymentMethod).toBe('pix')
    expect(store.error).toBeNull()
  })

  it('sends the status filter as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useSalesStore()
    store.setStatusFilter('paid')

    await store.fetchSales()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/sales',
      expect.objectContaining({ params: expect.objectContaining({ status: 'paid' }) }),
    )
  })

  it('setStatusFilter resets the page back to 1', () => {
    const store = useSalesStore()
    store.setPage(4)
    store.setStatusFilter('open')
    expect(store.page).toBe(1)
  })

  it('createSale posts the snake_case payload and returns the mapped sale', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SALE } })
    const store = useSalesStore()

    const created = await store.createSale({ customerId: 'customer-1', paymentMethod: 'pix' })

    expect(created?.paymentMethod).toBe('pix')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/sales',
      expect.objectContaining({ customer_id: 'customer-1', payment_method: 'pix' }),
    )
  })

  it('updateSale patches discount and returns the recalculated total', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_SALE, discount: '20.00', total: '80.00' } },
    })
    const store = useSalesStore()

    const result = await store.updateSale('sale-1', { discount: 20 })

    expect(result?.total).toBe(80)
    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/sales/sale-1',
      expect.objectContaining({ discount: 20 }),
    )
  })

  it('addItem posts product_id and returns the mapped item', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ITEM } })
    const store = useSalesStore()

    const item = await store.addItem('sale-1', { productId: 'product-1', quantity: 2 })

    expect(item?.total).toBe(980)
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/sales/sale-1/items',
      expect.objectContaining({ product_id: 'product-1', quantity: 2 }),
    )
  })

  it('addItem returns null and sets error when the sale is locked', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(
      buildError(422, "Não é possível alterar uma Venda 'paid'."),
    )
    const store = useSalesStore()

    const item = await store.addItem('sale-1', { productId: 'product-1', quantity: 1 })

    expect(item).toBeNull()
    expect(store.error).toContain('Não é possível alterar uma Venda')
  })

  it('removeItem returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useSalesStore()

    const success = await store.removeItem('sale-1', 'item-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/sales/sale-1/items/item-1')
  })

  it('completeSale posts to the complete action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_SALE, status: 'paid' } },
    })
    const store = useSalesStore()

    const result = await store.completeSale('sale-1')

    expect(result?.status).toBe('paid')
    expect(http.post).toHaveBeenCalledWith('/api/v1/sales/sale-1/complete')
  })

  it('completeSale returns null and sets error on insufficient stock', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(
      buildError(409, 'Estoque insuficiente para esta movimentação.'),
    )
    const store = useSalesStore()

    const result = await store.completeSale('sale-1')

    expect(result).toBeNull()
    expect(store.error).toContain('Estoque insuficiente')
  })

  it('cancelSale posts to the cancel action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_SALE, status: 'cancelled' } },
    })
    const store = useSalesStore()

    const result = await store.cancelSale('sale-1')

    expect(result?.status).toBe('cancelled')
    expect(http.post).toHaveBeenCalledWith('/api/v1/sales/sale-1/cancel')
  })

  it('getSale returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useSalesStore()

    const sale = await store.getSale('missing-id')

    expect(sale).toBeNull()
  })
})
