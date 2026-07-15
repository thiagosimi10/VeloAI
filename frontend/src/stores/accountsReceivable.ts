import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type AccountReceivableStatus = 'pending' | 'received' | 'cancelled'

export interface AccountReceivable {
  id: string
  customerId: string
  dueDate: string
  amount: number
  status: AccountReceivableStatus
  paymentDate: string | null
  isOverdue: boolean
}

export interface AccountReceivableFormPayload {
  customerId: string
  dueDate: string
  amount: number
}

export interface UpdateAccountReceivablePayload {
  dueDate?: string
  amount?: number
}

interface RawAccountReceivable {
  id: string
  customer_id: string
  due_date: string
  amount: string
  status: AccountReceivableStatus
  payment_date: string | null
  is_overdue: boolean
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface AccountsReceivableState {
  items: AccountReceivable[]
  meta: PaginationMeta
  status: AccountReceivableStatus | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapReceivable(raw: RawAccountReceivable): AccountReceivable {
  return {
    id: raw.id,
    customerId: raw.customer_id,
    dueDate: raw.due_date,
    amount: Number(raw.amount),
    status: raw.status,
    paymentDate: raw.payment_date,
    isOverdue: raw.is_overdue,
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

export const useAccountsReceivableStore = defineStore('accountsReceivable', {
  state: (): AccountsReceivableState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    status: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setStatusFilter(value: AccountReceivableStatus | null): void {
      this.status = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async fetchReceivables(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawAccountReceivable[]; meta: PaginationMeta }>(
          '/api/v1/accounts-receivable',
          { params: { status: this.status || undefined, page: this.page } },
        )
        this.items = response.data.data.map(mapReceivable)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async getReceivable(id: string): Promise<AccountReceivable | null> {
      try {
        const response = await http.get<{ data: RawAccountReceivable }>(
          `/api/v1/accounts-receivable/${id}`,
        )
        return mapReceivable(response.data.data)
      } catch {
        return null
      }
    },

    async createReceivable(
      payload: AccountReceivableFormPayload,
    ): Promise<AccountReceivable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountReceivable }>(
          '/api/v1/accounts-receivable',
          {
            customer_id: payload.customerId,
            due_date: payload.dueDate,
            amount: payload.amount,
          },
        )
        return mapReceivable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateReceivable(
      id: string,
      payload: UpdateAccountReceivablePayload,
    ): Promise<AccountReceivable | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawAccountReceivable }>(
          `/api/v1/accounts-receivable/${id}`,
          { due_date: payload.dueDate, amount: payload.amount },
        )
        return mapReceivable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async receiveReceivable(id: string): Promise<AccountReceivable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountReceivable }>(
          `/api/v1/accounts-receivable/${id}/receive`,
        )
        return mapReceivable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async cancelReceivable(id: string): Promise<AccountReceivable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountReceivable }>(
          `/api/v1/accounts-receivable/${id}/cancel`,
        )
        return mapReceivable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
