import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useDashboardStore } from '@/stores/dashboard'

const RAW_SUMMARY = {
  total_customers: 10,
  total_products: 20,
  total_services: 5,
  orders_by_status: { open: 2, in_progress: 1, completed: 8, cancelled: 1 },
  revenue_this_month: '1100.00',
  revenue_last_month: '1000.00',
  revenue_change_percentage: '10.00',
  average_ticket: '275.00',
  accounts_receivable_pending_total: '500.00',
  accounts_receivable_overdue_count: 1,
  accounts_payable_pending_total: '200.00',
  accounts_payable_overdue_count: 0,
  cash_balance: '3000.00',
  critical_stock_count: 2,
}

describe('dashboard store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('fetches and maps the summary, converting decimal strings to numbers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUMMARY } })
    const store = useDashboardStore()

    await store.fetchSummary()

    expect(store.summary?.totalCustomers).toBe(10)
    expect(store.summary?.revenueThisMonth).toBe(1100)
    expect(store.summary?.revenueChangePercentage).toBe(10)
    expect(store.summary?.ordersByStatus).toEqual({
      open: 2,
      in_progress: 1,
      completed: 8,
      cancelled: 1,
    })
    expect(store.error).toBeNull()
  })

  it('maps a null revenue change percentage without converting it to a number', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: { ...RAW_SUMMARY, revenue_change_percentage: null } },
    })
    const store = useDashboardStore()

    await store.fetchSummary()

    expect(store.summary?.revenueChangePercentage).toBeNull()
  })

  it('sets an error message when fetchSummary fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('failed'))
    const store = useDashboardStore()

    await store.fetchSummary()

    expect(store.summary).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('fetches and maps the revenue timeseries', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: {
        data: [
          { period: '2026-02', revenue: '500.00' },
          { period: '2026-03', revenue: '700.00' },
        ],
      },
    })
    const store = useDashboardStore()

    await store.fetchRevenueTimeseries()

    expect(store.revenueTimeseries).toHaveLength(2)
    expect(store.revenueTimeseries[1]?.revenue).toBe(700)
  })

  it('fetches and maps the top products', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [{ product_id: 'product-1', name: 'SSD Kingston 1TB', quantity_sold: 15 }] },
    })
    const store = useDashboardStore()

    await store.fetchTopProducts()

    expect(store.topProducts).toHaveLength(1)
    expect(store.topProducts[0]?.quantitySold).toBe(15)
    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/dashboard/top-products',
      expect.objectContaining({ params: { limit: 5 } }),
    )
  })
})
