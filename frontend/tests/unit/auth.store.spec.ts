import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn(), get: vi.fn(), patch: vi.fn() },
}))

import { http } from '@/services/http'
import { useAuthStore } from '@/stores/auth'

const RAW_USER = {
  id: 'user-1',
  email: 'maria@empresa.test',
  first_name: 'Maria',
  last_name: 'Souza',
  role: 'Administrador',
  permissions: ['system.admin'],
  must_change_password: true,
}

function build404Error(): AxiosError {
  return new AxiosError('Not Found', '404', undefined, undefined, {
    status: 404,
    statusText: 'Not Found',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: {},
  } as never)
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
    vi.mocked(http.get).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('starts unauthenticated and not bootstrapped', () => {
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(false)
    expect(store.isBootstrapped).toBe(false)
  })

  it('loads the user profile and becomes authenticated on successful login', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_USER } })
    const store = useAuthStore()

    const success = await store.login({ email: 'maria@empresa.test', password: 'Temp0rary!' })

    expect(success).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.email).toBe('maria@empresa.test')
    expect(store.user?.firstName).toBe('Maria')
    expect(store.user?.mustChangePassword).toBe(true)
    expect(store.hasPermission('system.admin')).toBe(true)
    expect(store.hasPermission('customers.view')).toBe(false)
    expect(store.error).toBeNull()
  })

  it('exposes a friendly message when the login endpoint does not exist yet (404)', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(build404Error())
    const store = useAuthStore()

    const success = await store.login({ email: 'a@a.com', password: '123456' })

    expect(success).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.error).toContain('não está disponível')
  })

  it('exposes an invalid credentials message from the backend response', async () => {
    const error = new AxiosError('Unauthorized', '401', undefined, undefined, {
      status: 401,
      statusText: 'Unauthorized',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { message: 'E-mail ou senha inválidos.' },
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const store = useAuthStore()

    const success = await store.login({ email: 'a@a.com', password: 'wrong' })

    expect(success).toBe(false)
    expect(store.error).toBe('E-mail ou senha inválidos.')
  })

  it('fetchCurrentUser restores the session and marks it as bootstrapped', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_USER } })
    const store = useAuthStore()

    const success = await store.fetchCurrentUser()

    expect(success).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.isBootstrapped).toBe(true)
  })

  it('fetchCurrentUser clears the user when there is no valid session', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(build404Error())
    const store = useAuthStore()

    const success = await store.fetchCurrentUser()

    expect(success).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.isBootstrapped).toBe(true)
  })

  it('changePassword clears the mustChangePassword flag on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_USER } })
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: {} } })
    const store = useAuthStore()
    await store.login({ email: 'maria@empresa.test', password: 'Temp0rary!' })

    const success = await store.changePassword({
      currentPassword: 'Temp0rary!',
      newPassword: 'NovaSenhaForte123!',
    })

    expect(success).toBe(true)
    expect(store.user?.mustChangePassword).toBe(false)
    expect(http.patch).toHaveBeenCalledWith('/api/v1/auth/password', {
      current_password: 'Temp0rary!',
      new_password: 'NovaSenhaForte123!',
    })
  })

  it('logout clears the user and error state', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_USER } })
    const store = useAuthStore()
    await store.login({ email: 'maria@empresa.test', password: 'Temp0rary!' })

    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: {} } })
    await store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('logout clears local state even if the request fails', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_USER } })
    const store = useAuthStore()
    await store.login({ email: 'maria@empresa.test', password: 'Temp0rary!' })

    vi.mocked(http.post).mockRejectedValueOnce(new Error('network error'))
    await store.logout()

    expect(store.isAuthenticated).toBe(false)
  })
})
