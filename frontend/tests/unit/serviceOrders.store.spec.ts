import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useServiceOrdersStore } from '@/stores/serviceOrders'

function buildError(status: number, message: string): AxiosError {
  return new AxiosError('Error', String(status), undefined, undefined, {
    status,
    statusText: 'Error',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_ORDER = {
  id: 'order-1',
  number: 'OS-2026-000001',
  customer_id: 'customer-1',
  technician_id: null,
  status: 'open' as const,
  equipment: 'Notebook Dell',
  serial_number: null,
  problem: 'Não liga',
  diagnosis: null,
  solution: null,
  total: '0.00',
  opened_at: '2026-01-01T00:00:00Z',
  finished_at: null,
  items: [],
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

describe('service orders store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps orders, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_ORDER], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useServiceOrdersStore()

    await store.fetchOrders()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.total).toBe(0)
    expect(store.items[0]?.number).toBe('OS-2026-000001')
    expect(store.error).toBeNull()
  })

  it('sends the status filter as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useServiceOrdersStore()
    store.setStatusFilter('in_progress')

    await store.fetchOrders()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/service-orders',
      expect.objectContaining({ params: expect.objectContaining({ status: 'in_progress' }) }),
    )
  })

  it('setSearch and setStatusFilter reset the page back to 1', () => {
    const store = useServiceOrdersStore()
    store.setPage(3)
    store.setSearch('OS-2026')
    expect(store.page).toBe(1)

    store.setPage(4)
    store.setStatusFilter('open')
    expect(store.page).toBe(1)
  })

  it('createOrder posts the snake_case payload and returns the mapped order', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ORDER } })
    const store = useServiceOrdersStore()

    const created = await store.createOrder({ customerId: 'customer-1', equipment: 'Notebook Dell' })

    expect(created?.number).toBe('OS-2026-000001')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/service-orders',
      expect.objectContaining({ customer_id: 'customer-1', equipment: 'Notebook Dell' }),
    )
  })

  it('addItem posts product_id or service_id and returns the mapped item', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ITEM } })
    const store = useServiceOrdersStore()

    const item = await store.addItem('order-1', { productId: 'product-1', quantity: 2 })

    expect(item?.total).toBe(980)
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/service-orders/order-1/items',
      expect.objectContaining({ product_id: 'product-1', service_id: null, quantity: 2 }),
    )
  })

  it('addItem returns null and sets error when the order is locked', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(
      buildError(422, 'Não é possível alterar itens de uma Ordem de Serviço \'completed\'.'),
    )
    const store = useServiceOrdersStore()

    const item = await store.addItem('order-1', { productId: 'product-1', quantity: 1 })

    expect(item).toBeNull()
    expect(store.error).toContain('Não é possível alterar itens')
  })

  it('removeItem returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useServiceOrdersStore()

    const success = await store.removeItem('order-1', 'item-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/service-orders/order-1/items/item-1')
  })

  it('startOrder posts to the start action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_ORDER, status: 'in_progress' } },
    })
    const store = useServiceOrdersStore()

    const result = await store.startOrder('order-1')

    expect(result?.status).toBe('in_progress')
    expect(http.post).toHaveBeenCalledWith('/api/v1/service-orders/order-1/start')
  })

  it('closeOrder posts technician_id and solution', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_ORDER, status: 'completed' } },
    })
    const store = useServiceOrdersStore()

    const result = await store.closeOrder('order-1', {
      technicianId: 'user-1',
      solution: 'Placa trocada',
    })

    expect(result?.status).toBe('completed')
    expect(http.post).toHaveBeenCalledWith('/api/v1/service-orders/order-1/close', {
      technician_id: 'user-1',
      solution: 'Placa trocada',
    })
  })

  it('closeOrder returns null and sets error when technician is missing', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(
      buildError(422, 'Não é possível concluir uma Ordem de Serviço sem técnico responsável.'),
    )
    const store = useServiceOrdersStore()

    const result = await store.closeOrder('order-1', {})

    expect(result).toBeNull()
    expect(store.error).toContain('técnico responsável')
  })

  it('cancelOrder posts to the cancel action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_ORDER, status: 'cancelled' } },
    })
    const store = useServiceOrdersStore()

    const result = await store.cancelOrder('order-1')

    expect(result?.status).toBe('cancelled')
    expect(http.post).toHaveBeenCalledWith('/api/v1/service-orders/order-1/cancel')
  })

  it('getOrder returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useServiceOrdersStore()

    const order = await store.getOrder('missing-id')

    expect(order).toBeNull()
  })
})
