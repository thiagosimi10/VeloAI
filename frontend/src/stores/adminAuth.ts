import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface PlatformAdmin {
  id: string
  email: string
  firstName: string
  lastName: string | null
  mustChangePassword: boolean
}

interface RawPlatformAdmin {
  id: string
  email: string
  first_name: string
  last_name: string | null
  must_change_password: boolean
}

interface AdminLoginCredentials {
  email: string
  password: string
}

interface ChangeAdminPasswordPayload {
  currentPassword: string
  newPassword: string
}

interface AdminAuthState {
  admin: PlatformAdmin | null
  isLoading: boolean
  isBootstrapped: boolean
  error: string | null
}

function mapAdmin(raw: RawPlatformAdmin): PlatformAdmin {
  return {
    id: raw.id,
    email: raw.email,
    firstName: raw.first_name,
    lastName: raw.last_name,
    mustChangePassword: raw.must_change_password,
  }
}

function extractErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const message = (error.response?.data as { message?: unknown } | undefined)?.message
    if (typeof message === 'string') {
      return message
    }
  }
  return 'Não foi possível conectar ao servidor. Tente novamente.'
}

/**
 * Sessão de Platform Admin — totalmente separada de `stores/auth.ts` (sessão de
 * tenant). Nunca compartilha cookie/estado com o login de tenant, mesmo no mesmo
 * navegador (docs/34-MASTER-PLAN.md, Fase 18).
 */
export const useAdminAuthStore = defineStore('adminAuth', {
  state: (): AdminAuthState => ({
    admin: null,
    isLoading: false,
    isBootstrapped: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state): boolean => state.admin !== null,
  },
  actions: {
    async login(credentials: AdminLoginCredentials): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: RawPlatformAdmin }>(
          '/api/v1/admin/auth/login',
          credentials,
        )
        this.admin = mapAdmin(response.data.data)
        return true
      } catch (error) {
        this.admin = null
        this.error = extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
        this.isBootstrapped = true
      }
    },

    async fetchCurrentAdmin(): Promise<boolean> {
      try {
        const response = await http.get<{ data: RawPlatformAdmin }>('/api/v1/admin/auth/me')
        this.admin = mapAdmin(response.data.data)
        return true
      } catch {
        this.admin = null
        return false
      } finally {
        this.isBootstrapped = true
      }
    },

    async changePassword(payload: ChangeAdminPasswordPayload): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        await http.patch('/api/v1/admin/auth/password', {
          current_password: payload.currentPassword,
          new_password: payload.newPassword,
        })
        if (this.admin) {
          this.admin = { ...this.admin, mustChangePassword: false }
        }
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
      }
    },

    async logout(): Promise<void> {
      try {
        await http.post('/api/v1/admin/auth/logout')
      } catch {
        // Logout sempre limpa o estado local, mesmo que a chamada ao Backend falhe.
      } finally {
        this.admin = null
      }
    },
  },
})
