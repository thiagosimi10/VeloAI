import { defineStore } from 'pinia'
import { isAxiosError } from 'axios'

import { http } from '@/services/http'

interface LoginCredentials {
  email: string
  password: string
}

interface AuthState {
  accessToken: string | null
  isLoading: boolean
  error: string | null
}

/**
 * Nesta fase de fundação o endpoint `/api/v1/auth/login` ainda não existe no Backend
 * (Autenticação é a Fase 3 do Master Plan). Esta store já está pronta para a integração
 * real, mas hoje qualquer tentativa de login falhará com um erro tratado — nunca
 * simulamos um login bem-sucedido no Frontend.
 */
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: null,
    isLoading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state): boolean => Boolean(state.accessToken),
  },
  actions: {
    async login(credentials: LoginCredentials): Promise<boolean> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: { access_token: string } }>(
          '/api/v1/auth/login',
          credentials,
        )
        this.accessToken = response.data.data.access_token
        return true
      } catch (error) {
        this.accessToken = null
        this.error = this._extractErrorMessage(error)
        return false
      } finally {
        this.isLoading = false
      }
    },
    logout(): void {
      this.accessToken = null
      this.error = null
    },
    _extractErrorMessage(error: unknown): string {
      if (isAxiosError(error)) {
        const message = error.response?.data?.message
        if (typeof message === 'string') {
          return message
        }
        if (error.response?.status === 404) {
          return 'Login ainda não está disponível nesta fase do sistema.'
        }
      }
      return 'Não foi possível conectar ao servidor. Tente novamente.'
    },
  },
})
