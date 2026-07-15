import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type ServiceOrderStatus = 'open' | 'in_progress' | 'completed' | 'cancelled'

export interface ServiceOrderItem {
  id: string
  serviceOrderId: string
  productId: string | null
  serviceId: string | null
  quantity: number
  unitPrice: number
  total: number
}

export interface ServiceOrder {
  id: string
  number: string
  customerId: string
  technicianId: string | null
  status: ServiceOrderStatus
  equipment: string | null
  serialNumber: string | null
  problem: string | null
  diagnosis: string | null
  solution: string | null
  total: number
  openedAt: string
  finishedAt: string | null
  items: ServiceOrderItem[]
}

export interface ServiceOrderFormPayload {
  customerId: string
  technicianId?: string | null
  equipment?: string | null
  serialNumber?: string | null
  problem?: string | null
}

export interface AddServiceOrderItemPayload {
  productId?: string | null
  serviceId?: string | null
  quantity: number
  unitPrice?: number | null
}

export interface CloseServiceOrderPayload {
  technicianId?: string | null
  solution?: string | null
}

interface RawServiceOrderItem {
  id: string
  service_order_id: string
  product_id: string | null
  service_id: string | null
  quantity: number
  unit_price: string
  total: string
}

interface RawServiceOrder {
  id: string
  number: string
  customer_id: string
  technician_id: string | null
  status: ServiceOrderStatus
  equipment: string | null
  serial_number: string | null
  problem: string | null
  diagnosis: string | null
  solution: string | null
  total: string
  opened_at: string
  finished_at: string | null
  items: RawServiceOrderItem[]
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface ServiceOrdersState {
  items: ServiceOrder[]
  meta: PaginationMeta
  search: string
  status: ServiceOrderStatus | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapItem(raw: RawServiceOrderItem): ServiceOrderItem {
  return {
    id: raw.id,
    serviceOrderId: raw.service_order_id,
    productId: raw.product_id,
    serviceId: raw.service_id,
    quantity: raw.quantity,
    unitPrice: Number(raw.unit_price),
    total: Number(raw.total),
  }
}

function mapOrder(raw: RawServiceOrder): ServiceOrder {
  return {
    id: raw.id,
    number: raw.number,
    customerId: raw.customer_id,
    technicianId: raw.technician_id,
    status: raw.status,
    equipment: raw.equipment,
    serialNumber: raw.serial_number,
    problem: raw.problem,
    diagnosis: raw.diagnosis,
    solution: raw.solution,
    total: Number(raw.total),
    openedAt: raw.opened_at,
    finishedAt: raw.finished_at,
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

export const useServiceOrdersStore = defineStore('serviceOrders', {
  state: (): ServiceOrdersState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    search: '',
    status: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setSearch(value: string): void {
      this.search = value
      this.page = 1
    },

    setStatusFilter(value: ServiceOrderStatus | null): void {
      this.status = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async fetchOrders(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawServiceOrder[]; meta: PaginationMeta }>(
          '/api/v1/service-orders',
          {
            params: {
              search: this.search || undefined,
              status: this.status || undefined,
              page: this.page,
            },
          },
        )
        this.items = response.data.data.map(mapOrder)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async getOrder(id: string): Promise<ServiceOrder | null> {
      try {
        const response = await http.get<{ data: RawServiceOrder }>(`/api/v1/service-orders/${id}`)
        return mapOrder(response.data.data)
      } catch {
        return null
      }
    },

    async createOrder(payload: ServiceOrderFormPayload): Promise<ServiceOrder | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawServiceOrder }>('/api/v1/service-orders', {
          customer_id: payload.customerId,
          technician_id: payload.technicianId || null,
          equipment: payload.equipment || null,
          serial_number: payload.serialNumber || null,
          problem: payload.problem || null,
        })
        return mapOrder(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async addItem(
      orderId: string,
      payload: AddServiceOrderItemPayload,
    ): Promise<ServiceOrderItem | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawServiceOrderItem }>(
          `/api/v1/service-orders/${orderId}/items`,
          {
            product_id: payload.productId || null,
            service_id: payload.serviceId || null,
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

    async removeItem(orderId: string, itemId: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/service-orders/${orderId}/items/${itemId}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },

    async startOrder(orderId: string): Promise<ServiceOrder | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawServiceOrder }>(
          `/api/v1/service-orders/${orderId}/start`,
        )
        return mapOrder(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async closeOrder(
      orderId: string,
      payload: CloseServiceOrderPayload,
    ): Promise<ServiceOrder | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawServiceOrder }>(
          `/api/v1/service-orders/${orderId}/close`,
          {
            technician_id: payload.technicianId || null,
            solution: payload.solution || null,
          },
        )
        return mapOrder(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async cancelOrder(orderId: string): Promise<ServiceOrder | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawServiceOrder }>(
          `/api/v1/service-orders/${orderId}/cancel`,
        )
        return mapOrder(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },
  },
})
