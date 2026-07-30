import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface Service {
  id: string
  categoryId: string | null
  code: string
  name: string
  description: string | null
  estimatedTime: number | null
  price: number
  active: boolean
  createdAt: string
  updatedAt: string
}

export interface ServiceFormPayload {
  categoryId?: string | null
  name: string
  description?: string | null
  estimatedTime?: number | null
  price: number
  active: boolean
}

interface RawService {
  id: string
  category_id: string | null
  code: string
  name: string
  description: string | null
  estimated_time: number | null
  price: string
  active: boolean
  created_at: string
  updated_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface ServicesState {
  items: Service[]
  meta: PaginationMeta
  search: string
  categoryId: string | null
  page: number
  isLoading: boolean
  error: string | null
}

function mapService(raw: RawService): Service {
  return {
    id: raw.id,
    categoryId: raw.category_id,
    code: raw.code,
    name: raw.name,
    description: raw.description,
    estimatedTime: raw.estimated_time,
    price: Number(raw.price),
    active: raw.active,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  }
}

function toRawPayload(payload: ServiceFormPayload): Record<string, unknown> {
  return {
    category_id: payload.categoryId || null,
    name: payload.name,
    description: payload.description || null,
    estimated_time: payload.estimatedTime,
    price: payload.price,
    active: payload.active,
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

export const useServicesStore = defineStore('services', {
  state: (): ServicesState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    search: '',
    categoryId: null,
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchServices(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawService[]; meta: PaginationMeta }>(
          '/api/v1/services',
          {
            params: {
              search: this.search || undefined,
              category_id: this.categoryId || undefined,
              page: this.page,
            },
          },
        )
        this.items = response.data.data.map(mapService)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    setSearch(value: string): void {
      this.search = value
      this.page = 1
    },

    setCategoryFilter(value: string | null): void {
      this.categoryId = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async getService(id: string): Promise<Service | null> {
      try {
        const response = await http.get<{ data: RawService }>(`/api/v1/services/${id}`)
        return mapService(response.data.data)
      } catch {
        return null
      }
    },

    async createService(payload: ServiceFormPayload): Promise<Service | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawService }>(
          '/api/v1/services',
          toRawPayload(payload),
        )
        return mapService(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateService(id: string, payload: ServiceFormPayload): Promise<Service | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawService }>(
          `/api/v1/services/${id}`,
          toRawPayload(payload),
        )
        return mapService(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteService(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/services/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
