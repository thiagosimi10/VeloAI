import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/stores/auth'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn() },
}))

import { http } from '@/services/http'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('starts unauthenticated', () => {
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(false)
  })

  it('sets the access token and becomes authenticated on successful login', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { access_token: 'fake-token' } },
    })
    const store = useAuthStore()

    const success = await store.login({ email: 'a@a.com', password: '123456' })

    expect(success).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.error).toBeNull()
  })

  it('exposes a friendly message when the login endpoint does not exist yet (404)', async () => {
    const error = new AxiosError('Not Found', '404', undefined, undefined, {
      status: 404,
      statusText: 'Not Found',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: {},
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const store = useAuthStore()

    const success = await store.login({ email: 'a@a.com', password: '123456' })

    expect(success).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.error).toContain('não está disponível')
  })

  it('logout clears the token and error state', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { access_token: 'fake-token' } },
    })
    const store = useAuthStore()
    await store.login({ email: 'a@a.com', password: '123456' })

    store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.error).toBeNull()
  })
})
