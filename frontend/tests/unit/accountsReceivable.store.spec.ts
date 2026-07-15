import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAccountsReceivableStore } from '@/stores/accountsReceivable'

function buildError(status: number, message: string): AxiosError {
  return new AxiosError('Error', String(status), undefined, undefined, {
    status,
    statusText: 'Error',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_RECEIVABLE = {
  id: 'receivable-1',
  customer_id: 'customer-1',
  due_date: '2026-08-01',
  amount: '980.00',
  status: 'pending' as const,
  payment_date: null,
  is_overdue: false,
}

describe('accounts receivable store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('fetches and maps receivables, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_RECEIVABLE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useAccountsReceivableStore()

    await store.fetchReceivables()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.amount).toBe(980)
    expect(store.items[0]?.isOverdue).toBe(false)
    expect(store.error).toBeNull()
  })

  it('sends the status filter as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useAccountsReceivableStore()
    store.setStatusFilter('received')

    await store.fetchReceivables()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/accounts-receivable',
      expect.objectContaining({ params: expect.objectContaining({ status: 'received' }) }),
    )
  })

  it('createReceivable posts the snake_case payload and returns the mapped receivable', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_RECEIVABLE } })
    const store = useAccountsReceivableStore()

    const created = await store.createReceivable({
      customerId: 'customer-1',
      dueDate: '2026-08-01',
      amount: 980,
    })

    expect(created?.amount).toBe(980)
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/accounts-receivable',
      expect.objectContaining({ customer_id: 'customer-1', due_date: '2026-08-01', amount: 980 }),
    )
  })

  it('receiveReceivable posts to the receive action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_RECEIVABLE, status: 'received', payment_date: '2026-07-20' } },
    })
    const store = useAccountsReceivableStore()

    const result = await store.receiveReceivable('receivable-1')

    expect(result?.status).toBe('received')
    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-receivable/receivable-1/receive')
  })

  it('cancelReceivable posts to the cancel action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_RECEIVABLE, status: 'cancelled' } },
    })
    const store = useAccountsReceivableStore()

    const result = await store.cancelReceivable('receivable-1')

    expect(result?.status).toBe('cancelled')
    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-receivable/receivable-1/cancel')
  })

  it('updateReceivable returns null and sets error when not pending', async () => {
    vi.mocked(http.patch).mockRejectedValueOnce(
      buildError(422, "Não é possível alterar uma Conta a Receber 'received'."),
    )
    const store = useAccountsReceivableStore()

    const result = await store.updateReceivable('receivable-1', { amount: 500 })

    expect(result).toBeNull()
    expect(store.error).toContain('Não é possível alterar uma Conta a Receber')
  })

  it('getReceivable returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useAccountsReceivableStore()

    const receivable = await store.getReceivable('missing-id')

    expect(receivable).toBeNull()
  })
})
