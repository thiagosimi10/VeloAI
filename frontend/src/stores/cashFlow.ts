import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type CashFlowEntryType = 'in' | 'out'

export interface CashFlowEntry {
  id: string
  type: CashFlowEntryType
  category: string
  description: string | null
  amount: number
  date: string
  createdAt: string
}

export interface CashFlowEntryFormPayload {
  type: CashFlowEntryType
  category: string
  description?: string | null
  amount: number
}

interface RawCashFlowEntry {
  id: string
  type: CashFlowEntryType
  category: string
  description: string | null
  amount: string
  date: string
  created_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface CashFlowState {
  items: CashFlowEntry[]
  meta: PaginationMeta
  type: CashFlowEntryType | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapEntry(raw: RawCashFlowEntry): CashFlowEntry {
  return {
    id: raw.id,
    type: raw.type,
    category: raw.category,
    description: raw.description,
    amount: Number(raw.amount),
    date: raw.date,
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

export const useCashFlowStore = defineStore('cashFlow', {
  state: (): CashFlowState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    type: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setTypeFilter(value: CashFlowEntryType | null): void {
      this.type = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async fetchEntries(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawCashFlowEntry[]; meta: PaginationMeta }>(
          '/api/v1/cash-flow',
          { params: { type: this.type || undefined, page: this.page } },
        )
        this.items = response.data.data.map(mapEntry)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async createEntry(payload: CashFlowEntryFormPayload): Promise<CashFlowEntry | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawCashFlowEntry }>('/api/v1/cash-flow', {
          type: payload.type,
          category: payload.category,
          description: payload.description || null,
          amount: payload.amount,
        })
        return mapEntry(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
