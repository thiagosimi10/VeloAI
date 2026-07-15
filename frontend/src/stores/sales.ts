import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type SaleStatus = 'open' | 'paid' | 'cancelled'

export interface SaleItem {
  id: string
  saleId: string
  productId: string
  quantity: number
  unitPrice: number
  total: number
}

export interface Sale {
  id: string
  customerId: string
  status: SaleStatus
  paymentMethod: string | null
  discount: number
  total: number
  createdAt: string
  items: SaleItem[]
}

export interface SaleFormPayload {
  customerId: string
  paymentMethod?: string | null
}

export interface UpdateSalePayload {
  discount?: number | null
  paymentMethod?: string | null
}

export interface AddSaleItemPayload {
  productId: string
  quantity: number
  unitPrice?: number | null
}

interface RawSaleItem {
  id: string
  sale_id: string
  product_id: string
  quantity: number
  unit_price: string
  total: string
}

interface RawSale {
  id: string
  customer_id: string
  status: SaleStatus
  payment_method: string | null
  discount: string
  total: string
  created_at: string
  items: RawSaleItem[]
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface SalesState {
  items: Sale[]
  meta: PaginationMeta
  status: SaleStatus | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapItem(raw: RawSaleItem): SaleItem {
  return {
    id: raw.id,
    saleId: raw.sale_id,
    productId: raw.product_id,
    quantity: raw.quantity,
    unitPrice: Number(raw.unit_price),
    total: Number(raw.total),
  }
}

function mapSale(raw: RawSale): Sale {
  return {
    id: raw.id,
    customerId: raw.customer_id,
    status: raw.status,
    paymentMethod: raw.payment_method,
    discount: Number(raw.discount),
    total: Number(raw.total),
    createdAt: raw.created_at,
    items: (raw.items ?? []).map(mapItem),
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

export const useSalesStore = defineStore('sales', {
  state: (): SalesState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    status: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setStatusFilter(value: SaleStatus | null): void {
      this.status = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async fetchSales(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawSale[]; meta: PaginationMeta }>(
          '/api/v1/sales',
          {
            params: {
              status: this.status || undefined,
              page: this.page,
            },
          },
        )
        this.items = response.data.data.map(mapSale)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async getSale(id: string): Promise<Sale | null> {
      try {
        const response = await http.get<{ data: RawSale }>(`/api/v1/sales/${id}`)
        return mapSale(response.data.data)
      } catch {
        return null
      }
    },

    async createSale(payload: SaleFormPayload): Promise<Sale | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawSale }>('/api/v1/sales', {
          customer_id: payload.customerId,
          payment_method: payload.paymentMethod || null,
        })
        return mapSale(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateSale(saleId: string, payload: UpdateSalePayload): Promise<Sale | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawSale }>(`/api/v1/sales/${saleId}`, {
          discount: payload.discount ?? null,
          payment_method: payload.paymentMethod || null,
        })
        return mapSale(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async addItem(saleId: string, payload: AddSaleItemPayload): Promise<SaleItem | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawSaleItem }>(
          `/api/v1/sales/${saleId}/items`,
          {
            product_id: payload.productId,
            quantity: payload.quantity,
            unit_price: payload.unitPrice ?? null,
          },
        )
        return mapItem(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async removeItem(saleId: string, itemId: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/sales/${saleId}/items/${itemId}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async completeSale(saleId: string): Promise<Sale | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawSale }>(`/api/v1/sales/${saleId}/complete`)
        return mapSale(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async cancelSale(saleId: string): Promise<Sale | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawSale }>(`/api/v1/sales/${saleId}/cancel`)
        return mapSale(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
