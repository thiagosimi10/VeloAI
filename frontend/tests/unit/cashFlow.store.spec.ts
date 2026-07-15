import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useCashFlowStore } from '@/stores/cashFlow'

const RAW_ENTRY = {
  id: 'entry-1',
  type: 'in' as const,
  category: 'Recebimento',
  description: 'Recebimento da Conta a Receber receivable-1',
  amount: '980.00',
  date: '2026-07-20',
  created_at: '2026-07-20T10:00:00Z',
}

describe('cash flow store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('fetches and maps entries, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_ENTRY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useCashFlowStore()

    await store.fetchEntries()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.amount).toBe(980)
    expect(store.error).toBeNull()
  })

  it('sends the type filter as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useCashFlowStore()
    store.setTypeFilter('out')

    await store.fetchEntries()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/cash-flow',
      expect.objectContaining({ params: expect.objectContaining({ type: 'out' }) }),
    )
  })

  it('createEntry posts the snake_case payload and returns the mapped entry', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ENTRY } })
    const store = useCashFlowStore()

    const created = await store.createEntry({
      type: 'in',
      category: 'Recebimento',
      amount: 980,
    })

    expect(created?.amount).toBe(980)
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/cash-flow',
      expect.objectContaining({ type: 'in', category: 'Recebimento', amount: 980 }),
    )
  })

  it('createEntry returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useCashFlowStore()

    const result = await store.createEntry({ type: 'in', category: 'Recebimento', amount: 10 })

    expect(result).toBeNull()
    expect(store.error).not.toBeNull()
  })
})
