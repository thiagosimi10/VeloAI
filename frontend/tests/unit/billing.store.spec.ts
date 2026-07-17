import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useBillingStore } from '@/stores/billing'

const RAW_SUBSCRIPTION = {
  plan_name: 'VeloAI Professional',
  plan_price: '129.90',
  status: 'TRIAL',
  trial_ends_at: '2026-08-01T00:00:00Z',
  current_period_ends_at: null,
  days_remaining: 5,
}

describe('billing store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('fetches and maps the subscription', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUBSCRIPTION } })
    const store = useBillingStore()

    await store.fetchSubscription()

    expect(http.get).toHaveBeenCalledWith('/api/v1/billing/subscription')
    expect(store.subscription?.planName).toBe('VeloAI Professional')
    expect(store.subscription?.status).toBe('TRIAL')
    expect(store.subscription?.daysRemaining).toBe(5)
    expect(store.error).toBeNull()
  })

  it('fetchSubscription sets error on failure', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('failed'))
    const store = useBillingStore()

    await store.fetchSubscription()

    expect(store.subscription).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('cancelSubscription posts and updates the subscription on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_SUBSCRIPTION, status: 'CANCELED' } },
    })
    const store = useBillingStore()

    const success = await store.cancelSubscription()

    expect(success).toBe(true)
    expect(http.post).toHaveBeenCalledWith('/api/v1/billing/cancel')
    expect(store.subscription?.status).toBe('CANCELED')
  })

  it('cancelSubscription returns false and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useBillingStore()

    const success = await store.cancelSubscription()

    expect(success).toBe(false)
    expect(store.error).not.toBeNull()
  })
})
