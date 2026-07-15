import axios, { isAxiosError, type InternalAxiosRequestConfig } from 'axios'

/**
 * Instância única de comunicação com o Backend. O Frontend nunca acessa banco ou IA
 * diretamente — sempre através da API (docs/17-FRONTEND-ARCHITECTURE.md).
 *
 * `withCredentials: true` é obrigatório para que os cookies HttpOnly de
 * access/refresh token sejam enviados — o token nunca é lido ou armazenado em
 * JavaScript (docs/17-FRONTEND-ARCHITECTURE.md, docs/29-SECURITY.md).
 */
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
})

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

let refreshPromise: Promise<boolean> | null = null

async function refreshSession(): Promise<boolean> {
  refreshPromise ??= http
    .post('/api/v1/auth/refresh')
    .then(() => true)
    .catch(() => false)
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}

/**
 * Em um 401, tenta renovar a sessão silenciosamente uma única vez (via
 * `/auth/refresh`) e repete a requisição original — nunca para as próprias rotas de
 * login/refresh, para não entrar em loop.
 */
http.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!isAxiosError(error) || !error.config || error.response?.status !== 401) {
      return Promise.reject(error)
    }

    const originalRequest = error.config as RetryableRequestConfig
    const isAuthRoute =
      originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')

    if (isAuthRoute || originalRequest._retry) {
      return Promise.reject(error)
    }

    originalRequest._retry = true
    const refreshed = await refreshSession()
    if (refreshed) {
      return http(originalRequest)
    }

    return Promise.reject(error)
  },
)
