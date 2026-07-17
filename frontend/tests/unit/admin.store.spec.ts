import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAdminStore } from '@/stores/admin'

const RAW_SUMMARY = {
  total_tenants: 3,
  trial_count: 1,
  active_count: 2,
  pending_payment_count: 0,
  overdue_count: 0,
  suspended_count: 0,
  canceled_count: 0,
  expired_count: 0,
  estimated_mrr: '259.80',
}

const RAW_TENANT = {
  tenant_id: 'tenant-1',
  legal_name: 'Assistência Silva',
  document: '12345678000199',
  status: 'ACTIVE',
  plan_name: 'VeloAI Professional',
  subscription_status: 'ACTIVE',
  trial_ends_at: null,
}

const RAW_AUDIT_LOG_ENTRY = {
  id: 'log-1',
  action: 'SUBSCRIPTION_CANCELED',
  resource: 'subscriptions',
  before: { status: 'ACTIVE' },
  after: { status: 'CANCELED' },
  created_at: '2026-07-16T10:00:00Z',
}

describe('admin store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('fetches and maps the summary', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUMMARY } })
    const store = useAdminStore()

    await store.fetchSummary()

    expect(http.get).toHaveBeenCalledWith('/api/v1/admin/summary')
    expect(store.summary?.totalTenants).toBe(3)
    expect(store.summary?.estimatedMrr).toBe('259.80')
    expect(store.error).toBeNull()
  })

  it('fetchSummary sets an error on failure', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('failed'))
    const store = useAdminStore()

    await store.fetchSummary()

    expect(store.summary).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('fetches and maps tenants', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [RAW_TENANT] } })
    const store = useAdminStore()

    await store.fetchTenants()

    expect(http.get).toHaveBeenCalledWith('/api/v1/admin/tenants')
    expect(store.tenants).toHaveLength(1)
    expect(store.tenants[0]?.legalName).toBe('Assistência Silva')
    expect(store.tenants[0]?.planName).toBe('VeloAI Professional')
  })

  it('fetches and maps the audit log for a tenant', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_AUDIT_LOG_ENTRY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useAdminStore()

    await store.fetchAuditLog('tenant-1')

    expect(http.get).toHaveBeenCalledWith('/api/v1/admin/tenants/tenant-1/audit-log', {
      params: { page: 1 },
    })
    expect(store.auditLog).toHaveLength(1)
    expect(store.auditLog[0]?.action).toBe('SUBSCRIPTION_CANCELED')
    expect(store.auditLogMeta.total).toBe(1)
  })
})
