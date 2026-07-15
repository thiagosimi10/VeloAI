import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface TenantUserSummary {
  id: string
  firstName: string
  lastName: string | null
  email: string
  active: boolean
}

interface RawUser {
  id: string
  first_name: string
  last_name: string | null
  email: string
  active: boolean
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface UsersState {
  items: TenantUserSummary[]
  meta: PaginationMeta
  isLoading: boolean
  error: string | null
}

function mapUser(raw: RawUser): TenantUserSummary {
  return {
    id: raw.id,
    firstName: raw.first_name,
    lastName: raw.last_name,
    email: raw.email,
    active: raw.active,
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

export const useUsersStore = defineStore('users', {
  state: (): UsersState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchUsers(options: { pageSize?: number } = {}): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawUser[]; meta: PaginationMeta }>(
          '/api/v1/users',
          { params: { page_size: options.pageSize } },
        )
        this.items = response.data.data.map(mapUser)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },
  },
})
