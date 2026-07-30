import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface TenantOverview {
  tenantId: string
  legalName: string
  tradeName: string | null
  document: string
  status: string
  planName: string | null
  subscriptionStatus: string | null
  trialEndsAt: string | null
}

export interface CreateTenantPayload {
  legalName: string
  tradeName: string | null
  document: string
  adminName: string
  adminEmail: string
}

export interface UpdateTenantPayload {
  legalName: string
  tradeName: string | null
}

export interface TenantProvisioned {
  tenantId: string
  legalName: string
  document: string
  databaseName: string
  status: string
  admin: {
    adminEmail: string
    temporaryPassword: string
  }
}

export interface AdminSummary {
  totalTenants: number
  trialCount: number
  activeCount: number
  pendingPaymentCount: number
  overdueCount: number
  suspendedCount: number
  canceledCount: number
  expiredCount: number
  estimatedMrr: string
}

export interface AuditLogEntry {
  id: string
  action: string
  resource: string
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
  createdAt: string
}

interface RawTenantOverview {
  tenant_id: string
  legal_name: string
  trade_name: string | null
  document: string
  status: string
  plan_name: string | null
  subscription_status: string | null
  trial_ends_at: string | null
}

interface RawTenantProvisioned {
  tenant_id: string
  legal_name: string
  document: string
  database_name: string
  status: string
  admin: {
    admin_email: string
    temporary_password: string
  }
}

interface RawAdminSummary {
  total_tenants: number
  trial_count: number
  active_count: number
  pending_payment_count: number
  overdue_count: number
  suspended_count: number
  canceled_count: number
  expired_count: number
  estimated_mrr: string
}

interface RawAuditLogEntry {
  id: string
  action: string
  resource: string
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
  created_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface AdminState {
  summary: AdminSummary | null
  tenants: TenantOverview[]
  tenantsMeta: PaginationMeta
  tenantsSearch: string
  tenantsPage: number
  auditLog: AuditLogEntry[]
  auditLogMeta: PaginationMeta
  isLoading: boolean
  error: string | null
}

function mapTenant(raw: RawTenantOverview): TenantOverview {
  return {
    tenantId: raw.tenant_id,
    legalName: raw.legal_name,
    tradeName: raw.trade_name,
    document: raw.document,
    status: raw.status,
    planName: raw.plan_name,
    subscriptionStatus: raw.subscription_status,
    trialEndsAt: raw.trial_ends_at,
  }
}

function mapTenantProvisioned(raw: RawTenantProvisioned): TenantProvisioned {
  return {
    tenantId: raw.tenant_id,
    legalName: raw.legal_name,
    document: raw.document,
    databaseName: raw.database_name,
    status: raw.status,
    admin: {
      adminEmail: raw.admin.admin_email,
      temporaryPassword: raw.admin.temporary_password,
    },
  }
}

function mapSummary(raw: RawAdminSummary): AdminSummary {
  return {
    totalTenants: raw.total_tenants,
    trialCount: raw.trial_count,
    activeCount: raw.active_count,
    pendingPaymentCount: raw.pending_payment_count,
    overdueCount: raw.overdue_count,
    suspendedCount: raw.suspended_count,
    canceledCount: raw.canceled_count,
    expiredCount: raw.expired_count,
    estimatedMrr: raw.estimated_mrr,
  }
}

function mapAuditLogEntry(raw: RawAuditLogEntry): AuditLogEntry {
  return {
    id: raw.id,
    action: raw.action,
    resource: raw.resource,
    before: raw.before,
    after: raw.after,
    createdAt: raw.created_at,
  }
}

function extractErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const message = (error.response?.data as { message?: unknown } | undefined)?.message
    if (typeof message === 'string') {
      return message
    }
  }
  return 'Não foi possível concluir a operação. Tente novamente.'
}

export const useAdminStore = defineStore('admin', {
  state: (): AdminState => ({
    summary: null,
    tenants: [],
    tenantsMeta: { page: 1, page_size: 20, total: 0, pages: 0 },
    tenantsSearch: '',
    tenantsPage: 1,
    auditLog: [],
    auditLogMeta: { page: 1, page_size: 20, total: 0, pages: 0 },
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSummary(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawAdminSummary }>('/api/v1/admin/summary')
        this.summary = mapSummary(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async fetchTenants(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawTenantOverview[]; meta: PaginationMeta }>(
          '/api/v1/admin/tenants',
          {
            params: {
              search: this.tenantsSearch || undefined,
              page: this.tenantsPage,
            },
          },
        )
        this.tenants = response.data.data.map(mapTenant)
        this.tenantsMeta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    setTenantsSearch(search: string): void {
      this.tenantsSearch = search
      this.tenantsPage = 1
    },

    setTenantsPage(page: number): void {
      this.tenantsPage = page
    },

    async createTenant(payload: CreateTenantPayload): Promise<TenantProvisioned | null> {
      this.error = null

      try {
        const response = await http.post<{ data: RawTenantProvisioned }>('/api/v1/admin/tenants', {
          legal_name: payload.legalName,
          trade_name: payload.tradeName,
          document: payload.document,
          admin_name: payload.adminName,
          admin_email: payload.adminEmail,
        })
        return mapTenantProvisioned(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateTenant(tenantId: string, payload: UpdateTenantPayload): Promise<boolean> {
      this.error = null

      try {
        await http.patch(`/api/v1/admin/tenants/${tenantId}`, {
          legal_name: payload.legalName,
          trade_name: payload.tradeName,
        })
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async impersonateTenant(tenantId: string): Promise<boolean> {
      this.error = null

      try {
        await http.post(`/api/v1/admin/tenants/${tenantId}/impersonate`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async cancelTenant(tenantId: string): Promise<boolean> {
      this.error = null

      try {
        await http.post(`/api/v1/admin/tenants/${tenantId}/cancel`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async fetchAuditLog(tenantId: string, page = 1): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawAuditLogEntry[]; meta: PaginationMeta }>(
          `/api/v1/admin/tenants/${tenantId}/audit-log`,
          { params: { page } },
        )
        this.auditLog = response.data.data.map(mapAuditLogEntry)
        this.auditLogMeta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },
  },
})
