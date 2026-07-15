import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface DashboardSummary {
  totalCustomers: number
  totalProducts: number
  totalServices: number
  ordersByStatus: Record<string, number>
  revenueThisMonth: number
  revenueLastMonth: number
  revenueChangePercentage: number | null
  averageTicket: number
  accountsReceivablePendingTotal: number
  accountsReceivableOverdueCount: number
  accountsPayablePendingTotal: number
  accountsPayableOverdueCount: number
  cashBalance: number
  criticalStockCount: number
}

export interface RevenueTimeSeriesPoint {
  period: string
  revenue: number
}

export interface TopProductItem {
  productId: string
  name: string
  quantitySold: number
}

interface RawDashboardSummary {
  total_customers: number
  total_products: number
  total_services: number
  orders_by_status: Record<string, number>
  revenue_this_month: string
  revenue_last_month: string
  revenue_change_percentage: string | null
  average_ticket: string
  accounts_receivable_pending_total: string
  accounts_receivable_overdue_count: number
  accounts_payable_pending_total: string
  accounts_payable_overdue_count: number
  cash_balance: string
  critical_stock_count: number
}

interface RawRevenueTimeSeriesPoint {
  period: string
  revenue: string
}

interface RawTopProductItem {
  product_id: string
  name: string
  quantity_sold: number
}

interface DashboardState {
  summary: DashboardSummary | null
  revenueTimeseries: RevenueTimeSeriesPoint[]
  topProducts: TopProductItem[]
  isLoading: boolean
  error: string | null
}

function mapSummary(raw: RawDashboardSummary): DashboardSummary {
  return {
    totalCustomers: raw.total_customers,
    totalProducts: raw.total_products,
    totalServices: raw.total_services,
    ordersByStatus: raw.orders_by_status,
    revenueThisMonth: Number(raw.revenue_this_month),
    revenueLastMonth: Number(raw.revenue_last_month),
    revenueChangePercentage:
      raw.revenue_change_percentage === null ? null : Number(raw.revenue_change_percentage),
    averageTicket: Number(raw.average_ticket),
    accountsReceivablePendingTotal: Number(raw.accounts_receivable_pending_total),
    accountsReceivableOverdueCount: raw.accounts_receivable_overdue_count,
    accountsPayablePendingTotal: Number(raw.accounts_payable_pending_total),
    accountsPayableOverdueCount: raw.accounts_payable_overdue_count,
    cashBalance: Number(raw.cash_balance),
    criticalStockCount: raw.critical_stock_count,
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

export const useDashboardStore = defineStore('dashboard', {
  state: (): DashboardState => ({
    summary: null,
    revenueTimeseries: [],
    topProducts: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSummary(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawDashboardSummary }>('/api/v1/dashboard/summary')
        this.summary = mapSummary(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async fetchRevenueTimeseries(): Promise<void> {
      try {
        const response = await http.get<{ data: RawRevenueTimeSeriesPoint[] }>(
          '/api/v1/dashboard/revenue-timeseries',
        )
        this.revenueTimeseries = response.data.data.map((point) => ({
          period: point.period,
          revenue: Number(point.revenue),
        }))
      } catch (error) {
        this.error = extractErrorMessage(error)
      }
    },

    async fetchTopProducts(): Promise<void> {
      try {
        const response = await http.get<{ data: RawTopProductItem[] }>(
          '/api/v1/dashboard/top-products',
          { params: { limit: 5 } },
        )
        this.topProducts = response.data.data.map((item) => ({
          productId: item.product_id,
          name: item.name,
          quantitySold: item.quantity_sold,
        }))
      } catch (error) {
        this.error = extractErrorMessage(error)
      }
    },
  },
})
