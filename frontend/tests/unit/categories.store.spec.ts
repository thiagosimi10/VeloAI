import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useCategoriesStore } from '@/stores/categories'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_CATEGORY = {
  id: 'category-1',
  name: 'Armazenamento',
  description: 'SSDs e HDs',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('categories store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps categories with pagination meta', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CATEGORY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useCategoriesStore()

    await store.fetchCategories()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.name).toBe('Armazenamento')
    expect(store.meta.total).toBe(1)
    expect(store.error).toBeNull()
  })

  it('sends the pageSize option as page_size when provided', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
    })
    const store = useCategoriesStore()

    await store.fetchCategories({ pageSize: 100 })

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/categories',
      expect.objectContaining({ params: expect.objectContaining({ page_size: 100 }) }),
    )
  })

  it('setSearch resets the page back to 1', () => {
    const store = useCategoriesStore()
    store.setPage(3)

    store.setSearch('armazenamento')

    expect(store.page).toBe(1)
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useCategoriesStore()

    await store.fetchCategories()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createCategory posts the payload and returns the mapped category', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_CATEGORY } })
    const store = useCategoriesStore()

    const created = await store.createCategory({ name: 'Armazenamento', description: 'SSDs e HDs' })

    expect(created?.name).toBe('Armazenamento')
    expect(http.post).toHaveBeenCalledWith('/api/v1/categories', {
      name: 'Armazenamento',
      description: 'SSDs e HDs',
    })
  })

  it('createCategory returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(buildConflictError('Categoria já cadastrada.'))
    const store = useCategoriesStore()

    const created = await store.createCategory({ name: 'Armazenamento' })

    expect(created).toBeNull()
    expect(store.error).toBe('Categoria já cadastrada.')
  })

  it('updateCategory patches the given id', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: RAW_CATEGORY } })
    const store = useCategoriesStore()

    const updated = await store.updateCategory('category-1', { name: 'Armazenamento' })

    expect(updated).not.toBeNull()
    expect(http.patch).toHaveBeenCalledWith('/api/v1/categories/category-1', {
      name: 'Armazenamento',
    })
  })

  it('deleteCategory returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useCategoriesStore()

    const success = await store.deleteCategory('category-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/categories/category-1')
  })

  it('deleteCategory returns false and sets error on failure', async () => {
    vi.mocked(http.delete).mockRejectedValueOnce(new Error('network error'))
    const store = useCategoriesStore()

    const success = await store.deleteCategory('category-1')

    expect(success).toBe(false)
    expect(store.error).not.toBeNull()
  })

  it('getCategory returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useCategoriesStore()

    const category = await store.getCategory('missing-id')

    expect(category).toBeNull()
  })
})
