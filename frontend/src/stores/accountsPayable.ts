import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type AccountPayableStatus = 'pending' | 'paid' | 'cancelled'

export interface AccountPayable {
  id: string
  supplierId: string
  dueDate: string
  amount: number
  status: AccountPayableStatus
  paymentDate: string | null
  isOverdue: boolean
}

export interface AccountPayableFormPayload {
  supplierId: string
  dueDate: string
  amount: number
}

export interface UpdateAccountPayablePayload {
  dueDate?: string
  amount?: number
}

interface RawAccountPayable {
  id: string
  supplier_id: string
  due_date: string
  amount: string
  status: AccountPayableStatus
  payment_date: string | null
  is_overdue: boolean
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface AccountsPayableState {
  items: AccountPayable[]
  meta: PaginationMeta
  status: AccountPayableStatus | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapPayable(raw: RawAccountPayable): AccountPayable {
  return {
    id: raw.id,
    supplierId: raw.supplier_id,
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

export const useAccountsPayableStore = defineStore('accountsPayable', {
  state: (): AccountsPayableState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    status: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setStatusFilter(value: AccountPayableStatus | null): void {
      this.status = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async fetchPayables(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawAccountPayable[]; meta: PaginationMeta }>(
          '/api/v1/accounts-payable',
          { params: { status: this.status || undefined, page: this.page } },
        )
        this.items = response.data.data.map(mapPayable)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async getPayable(id: string): Promise<AccountPayable | null> {
      try {
        const response = await http.get<{ data: RawAccountPayable }>(
          `/api/v1/accounts-payable/${id}`,
        )
        return mapPayable(response.data.data)
      } catch {
        return null
      }
    },

    async createPayable(payload: AccountPayableFormPayload): Promise<AccountPayable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountPayable }>(
          '/api/v1/accounts-payable',
          {
            supplier_id: payload.supplierId,
            due_date: payload.dueDate,
            amount: payload.amount,
          },
        )
        return mapPayable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updatePayable(
      id: string,
      payload: UpdateAccountPayablePayload,
    ): Promise<AccountPayable | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawAccountPayable }>(
          `/api/v1/accounts-payable/${id}`,
          { due_date: payload.dueDate, amount: payload.amount },
        )
        return mapPayable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async payPayable(id: string): Promise<AccountPayable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountPayable }>(
          `/api/v1/accounts-payable/${id}/pay`,
        )
        return mapPayable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async cancelPayable(id: string): Promise<AccountPayable | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawAccountPayable }>(
          `/api/v1/accounts-payable/${id}/cancel`,
        )
        return mapPayable(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
