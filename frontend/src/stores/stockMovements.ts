import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type StockMovementType = 'in' | 'out' | 'adjustment'

export interface StockMovement {
  id: string
  productId: string
  movement: StockMovementType
  quantity: number
  previousStock: number
  currentStock: number
  reason: string
  createdAt: string
}

export interface StockMovementFormPayload {
  movement: StockMovementType
  quantity: number
  reason: string
}

interface RawStockMovement {
  id: string
  product_id: string
  movement: StockMovementType
  quantity: number
  previous_stock: number
  current_stock: number
  reason: string
  created_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface StockMovementsState {
  items: StockMovement[]
  meta: PaginationMeta
  page: number
  isLoading: boolean
  error: string | null
}

function mapMovement(raw: RawStockMovement): StockMovement {
  return {
    id: raw.id,
    productId: raw.product_id,
    movement: raw.movement,
    quantity: raw.quantity,
    previousStock: raw.previous_stock,
    currentStock: raw.current_stock,
    reason: raw.reason,
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

export const useStockMovementsStore = defineStore('stockMovements', {
  state: (): StockMovementsState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setPage(value: number): void {
      this.page = value
    },

    async fetchMovements(productId: string): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawStockMovement[]; meta: PaginationMeta }>(
          `/api/v1/products/${productId}/stock-movements`,
          { params: { page: this.page } },
        )
        this.items = response.data.data.map(mapMovement)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async createMovement(
      productId: string,
      payload: StockMovementFormPayload,
    ): Promise<StockMovement | null> {
      this.error = null
      try {
        // Envia uma cópia simples (não a referência reativa) — o chamador (ex.:
        // ProductStockView) reseta os campos do formulário logo após o sucesso, e uma
        // referência viva mutaria o payload já enviado.
        const response = await http.post<{ data: RawStockMovement }>(
          `/api/v1/products/${productId}/stock-movements`,
          {
            movement: payload.movement,
            quantity: payload.quantity,
            reason: payload.reason,
          },
        )
        return mapMovement(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
