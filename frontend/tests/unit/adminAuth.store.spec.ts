import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn(), get: vi.fn(), patch: vi.fn() },
}))

import { http } from '@/services/http'
import { useAdminAuthStore } from '@/stores/adminAuth'

const RAW_ADMIN = {
  id: 'admin-1',
  email: 'operador@veloai.internal',
  first_name: 'Operador',
  last_name: null,
  must_change_password: true,
}

describe('admin auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
    vi.mocked(http.get).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('starts unauthenticated and not bootstrapped', () => {
    const store = useAdminAuthStore()

    expect(store.isAuthenticated).toBe(false)
    expect(store.isBootstrapped).toBe(false)
  })

  it('loads the admin profile and becomes authenticated on successful login', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ADMIN } })
    const store = useAdminAuthStore()

    const success = await store.login({
      email: 'operador@veloai.internal',
      password: 'Sup3rSenha!',
    })

    expect(success).toBe(true)
    expect(http.post).toHaveBeenCalledWith('/api/v1/admin/auth/login', {
      email: 'operador@veloai.internal',
      password: 'Sup3rSenha!',
    })
    expect(store.isAuthenticated).toBe(true)
    expect(store.admin?.email).toBe('operador@veloai.internal')
    expect(store.admin?.mustChangePassword).toBe(true)
  })

  it('login sets an error and stays unauthenticated on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useAdminAuthStore()

    const success = await store.login({ email: 'a@a.com', password: 'wrong' })

    expect(success).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.error).not.toBeNull()
  })

  it('fetchCurrentAdmin restores the session and marks it as bootstrapped', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_ADMIN } })
    const store = useAdminAuthStore()

    const success = await store.fetchCurrentAdmin()

    expect(http.get).toHaveBeenCalledWith('/api/v1/admin/auth/me')
    expect(success).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.isBootstrapped).toBe(true)
  })

  it('fetchCurrentAdmin clears the admin when there is no valid session', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('unauthenticated'))
    const store = useAdminAuthStore()

    const success = await store.fetchCurrentAdmin()

    expect(success).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.isBootstrapped).toBe(true)
  })

  it('changePassword clears the mustChangePassword flag on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ADMIN } })
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: {} } })
    const store = useAdminAuthStore()
    await store.login({ email: 'operador@veloai.internal', password: 'Sup3rSenha!' })

    const success = await store.changePassword({
      currentPassword: 'Sup3rSenha!',
      newPassword: 'NovaSenha123!',
    })

    expect(success).toBe(true)
    expect(store.admin?.mustChangePassword).toBe(false)
    expect(http.patch).toHaveBeenCalledWith('/api/v1/admin/auth/password', {
      current_password: 'Sup3rSenha!',
      new_password: 'NovaSenha123!',
    })
  })

  it('logout clears local state even if the request fails', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ADMIN } })
    const store = useAdminAuthStore()
    await store.login({ email: 'operador@veloai.internal', password: 'Sup3rSenha!' })

    vi.mocked(http.post).mockRejectedValueOnce(new Error('network error'))
    await store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.admin).toBeNull()
  })
})
