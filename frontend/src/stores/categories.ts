import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface Category {
  id: string
  name: string
  description: string | null
  createdAt: string
  updatedAt: string
}

export interface CategoryFormPayload {
  name: string
  description?: string | null
}

interface RawCategory {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface CategoriesState {
  items: Category[]
  meta: PaginationMeta
  search: string
  page: number
  isLoading: boolean
  error: string | null
}

function mapCategory(raw: RawCategory): Category {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
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

export const useCategoriesStore = defineStore('categories', {
  state: (): CategoriesState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    search: '',
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCategories(options: { pageSize?: number } = {}): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawCategory[]; meta: PaginationMeta }>(
          '/api/v1/categories',
          {
            params: {
              search: this.search || undefined,
              page: this.page,
              page_size: options.pageSize,
            },
          },
        )
        this.items = response.data.data.map(mapCategory)
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

    setPage(value: number): void {
      this.page = value
    },

    async getCategory(id: string): Promise<Category | null> {
      try {
        const response = await http.get<{ data: RawCategory }>(`/api/v1/categories/${id}`)
        return mapCategory(response.data.data)
      } catch {
        return null
      }
    },

    async createCategory(payload: CategoryFormPayload): Promise<Category | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawCategory }>('/api/v1/categories', payload)
        return mapCategory(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateCategory(id: string, payload: CategoryFormPayload): Promise<Category | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawCategory }>(
          `/api/v1/categories/${id}`,
          payload,
        )
        return mapCategory(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteCategory(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/categories/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
