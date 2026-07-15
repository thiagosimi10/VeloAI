import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAccountsPayableStore } from '@/stores/accountsPayable'

function buildError(status: number, message: string): AxiosError {
  return new AxiosError('Error', String(status), undefined, undefined, {
    status,
    statusText: 'Error',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_PAYABLE = {
  id: 'payable-1',
  supplier_id: 'supplier-1',
  due_date: '2026-08-01',
  amount: '320.00',
  status: 'pending' as const,
  payment_date: null,
  is_overdue: false,
}

describe('accounts payable store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('fetches and maps payables, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_PAYABLE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useAccountsPayableStore()

    await store.fetchPayables()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.amount).toBe(320)
    expect(store.error).toBeNull()
  })

  it('sends the status filter as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useAccountsPayableStore()
    store.setStatusFilter('paid')

    await store.fetchPayables()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/accounts-payable',
      expect.objectContaining({ params: expect.objectContaining({ status: 'paid' }) }),
    )
  })

  it('createPayable posts the snake_case payload and returns the mapped payable', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_PAYABLE } })
    const store = useAccountsPayableStore()

    const created = await store.createPayable({
      supplierId: 'supplier-1',
      dueDate: '2026-08-01',
      amount: 320,
    })

    expect(created?.amount).toBe(320)
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/accounts-payable',
      expect.objectContaining({ supplier_id: 'supplier-1', due_date: '2026-08-01', amount: 320 }),
    )
  })

  it('payPayable posts to the pay action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_PAYABLE, status: 'paid', payment_date: '2026-07-20' } },
    })
    const store = useAccountsPayableStore()

    const result = await store.payPayable('payable-1')

    expect(result?.status).toBe('paid')
    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-payable/payable-1/pay')
  })

  it('cancelPayable posts to the cancel action', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_PAYABLE, status: 'cancelled' } },
    })
    const store = useAccountsPayableStore()

    const result = await store.cancelPayable('payable-1')

    expect(result?.status).toBe('cancelled')
    expect(http.post).toHaveBeenCalledWith('/api/v1/accounts-payable/payable-1/cancel')
  })

  it('updatePayable returns null and sets error when not pending', async () => {
    vi.mocked(http.patch).mockRejectedValueOnce(
      buildError(422, "Não é possível alterar uma Conta a Pagar 'paid'."),
    )
    const store = useAccountsPayableStore()

    const result = await store.updatePayable('payable-1', { amount: 500 })

    expect(result).toBeNull()
    expect(store.error).toContain('Não é possível alterar uma Conta a Pagar')
  })

  it('getPayable returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useAccountsPayableStore()

    const payable = await store.getPayable('missing-id')

    expect(payable).toBeNull()
  })
})
