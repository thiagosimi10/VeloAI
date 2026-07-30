import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface AuthUser {
  id: string
  email: string
  firstName: string
  lastName: string | null
  role: string
  permissions: string[]
  mustChangePassword: boolean
  tenantName: string
  avatarUrl: string | null
}

interface RawMeResponse {
  id: string
  email: string
  first_name: string
  last_name: string | null
  role: string
  permissions: string[]
  must_change_password: boolean
  tenant_name: string
  avatar_url: string | null
}

export interface UpdateProfilePayload {
  firstName: string
  lastName: string | null
}

interface LoginCredentials {
  email: string
  password: string
}

export interface SignupPayload {
  legalName: string
  tradeName: string | null
  document: string
  adminName: string
  adminEmail: string
  password: string
}

interface ChangePasswordPayload {
  currentPassword: string
  newPassword: string
}

interface AuthState {
  user: AuthUser | null
  isLoading: boolean
  isBootstrapped: boolean
  error: string | null
}

function mapUser(raw: RawMeResponse): AuthUser {
  return {
    id: raw.id,
    email: raw.email,
    firstName: raw.first_name,
    lastName: raw.last_name,
    role: raw.role,
    permissions: raw.permissions,
    mustChangePassword: raw.must_change_password,
    tenantName: raw.tenant_name,
    avatarUrl: raw.avatar_url,
  }
}

/**
 * O access/refresh token nunca fica acessível a este store (cookies HttpOnly) —
 * `isAuthenticated` é derivado apenas da presença de um perfil de usuário carregado via
 * `/auth/me` ou `/auth/login`.
 */
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isLoading: false,
    isBootstrapped: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state): boolean => state.user !== null,
    hasPermission:
      (state) =>
      (permission: string): boolean =>
        state.user?.permissions.includes(permission) ?? false,
  },
  actions: {
    async login(credentials: LoginCredentials): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: RawMeResponse }>(
          '/api/v1/auth/login',
          credentials,
        )
        this.user = mapUser(response.data.data)
        return true
      } catch (error) {
        this.user = null
        this.error = this._extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
        this.isBootstrapped = true
      }
    },

    async signup(payload: SignupPayload): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: RawMeResponse }>('/api/v1/auth/signup', {
          legal_name: payload.legalName,
          trade_name: payload.tradeName,
          document: payload.document,
          admin_name: payload.adminName,
          admin_email: payload.adminEmail,
          password: payload.password,
          website: '',
        })
        this.user = mapUser(response.data.data)
        return true
      } catch (error) {
        this.user = null
        this.error = this._extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
        this.isBootstrapped = true
      }
    },

    /** Restaura a sessão a partir do cookie HttpOnly após um reload de página. */
    async fetchCurrentUser(): Promise<boolean> {
      try {
        const response = await http.get<{ data: RawMeResponse }>('/api/v1/auth/me')
        this.user = mapUser(response.data.data)
        return true
      } catch {
        this.user = null
        return false
      } finally {
        this.isBootstrapped = true
      }
    },

    async changePassword(payload: ChangePasswordPayload): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        await http.patch('/api/v1/auth/password', {
          current_password: payload.currentPassword,
          new_password: payload.newPassword,
        })
        if (this.user) {
          this.user = { ...this.user, mustChangePassword: false }
        }
        return true
      } catch (error) {
        this.error = this._extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
      }
    },

    async updateProfile(payload: UpdateProfilePayload): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        await http.patch('/api/v1/auth/profile', {
          first_name: payload.firstName,
          last_name: payload.lastName || null,
        })
        if (this.user) {
          this.user = { ...this.user, firstName: payload.firstName, lastName: payload.lastName }
        }
        return true
      } catch (error) {
        this.error = this._extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
      }
    },

    async uploadAvatar(file: File): Promise<boolean> {
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await http.post<{ data: { avatar_url: string | null } }>(
          '/api/v1/auth/avatar',
          formData,
        )
        if (this.user) {
          this.user = { ...this.user, avatarUrl: response.data.data.avatar_url }
        }
        return true
      } catch (error) {
        this.error = this._extractErrorMessage(error)
        return false
      }
    },

    async logout(): Promise<void> {
      try {
        await http.post('/api/v1/auth/logout')
      } catch {
        // Logout sempre limpa o estado local, mesmo que a chamada ao Backend falhe
        // (ex.: sessão já expirada) — nunca prende o usuário na tela por causa disso.
      } finally {
        this.user = null
      }
    },

    _extractErrorMessage(error: unknown): string {
      if (isAxiosError(error)) {
        const message = (error.response?.data as { message?: unknown } | undefined)?.message
        if (typeof message === 'string') {
          return message
        }
        if (error.response?.status === 404) {
          return 'Este recurso ainda não está disponível nesta fase do sistema.'
        }
      }
      return 'Não foi possível conectar ao servidor. Tente novamente.'
    },
  },
})
