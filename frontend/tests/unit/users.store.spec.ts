import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useUsersStore } from '@/stores/users'

const RAW_USER = {
  id: 'user-1',
  first_name: 'Carlos',
  last_name: 'Souza',
  email: 'carlos@empresa.test',
  active: true,
}

describe('users store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  it('fetches and maps users', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_USER], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useUsersStore()

    await store.fetchUsers()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.firstName).toBe('Carlos')
    expect(store.error).toBeNull()
  })

  it('sends the pageSize option as page_size when provided', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
    })
    const store = useUsersStore()

    await store.fetchUsers({ pageSize: 100 })

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/users',
      expect.objectContaining({ params: expect.objectContaining({ page_size: 100 }) }),
    )
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useUsersStore()

    await store.fetchUsers()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })
})
