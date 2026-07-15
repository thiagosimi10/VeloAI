import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useServicesStore } from '@/stores/services'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_SERVICE = {
  id: 'service-1',
  category_id: 'category-1',
  code: 'S000001',
  name: 'Formatação de Computador',
  description: null,
  estimated_time: 60,
  price: '180.00',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('services store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps services, converting the price string to a number', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_SERVICE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useServicesStore()

    await store.fetchServices()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.price).toBe(180)
    expect(store.items[0]?.estimatedTime).toBe(60)
    expect(store.error).toBeNull()
  })

  it('sends the category filter as category_id', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useServicesStore()
    store.setCategoryFilter('category-1')

    await store.fetchServices()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/services',
      expect.objectContaining({ params: expect.objectContaining({ category_id: 'category-1' }) }),
    )
  })

  it('setSearch and setCategoryFilter reset the page back to 1', () => {
    const store = useServicesStore()
    store.setPage(3)
    store.setSearch('formatação')
    expect(store.page).toBe(1)

    store.setPage(4)
    store.setCategoryFilter('category-1')
    expect(store.page).toBe(1)
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useServicesStore()

    await store.fetchServices()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createService posts the snake_case payload and returns the mapped service', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SERVICE } })
    const store = useServicesStore()

    const created = await store.createService({
      name: 'Formatação de Computador',
      price: 180,
      estimatedTime: 60,
    })

    expect(created?.code).toBe('S000001')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/services',
      expect.objectContaining({ name: 'Formatação de Computador', price: 180 }),
    )
  })

  it('createService returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(buildConflictError('Não foi possível criar.'))
    const store = useServicesStore()

    const created = await store.createService({
      name: 'Formatação de Computador',
      price: 180,
    })

    expect(created).toBeNull()
    expect(store.error).toBe('Não foi possível criar.')
  })

  it('updateService patches the given id', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: RAW_SERVICE } })
    const store = useServicesStore()

    const updated = await store.updateService('service-1', {
      name: 'Formatação de Computador',
      price: 220,
    })

    expect(updated).not.toBeNull()
    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/services/service-1',
      expect.objectContaining({ price: 220 }),
    )
  })

  it('deleteService returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useServicesStore()

    const success = await store.deleteService('service-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/services/service-1')
  })

  it('getService returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useServicesStore()

    const service = await store.getService('missing-id')

    expect(service).toBeNull()
  })
})
