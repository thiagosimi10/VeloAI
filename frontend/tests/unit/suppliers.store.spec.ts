import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useSuppliersStore } from '@/stores/suppliers'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_SUPPLIER = {
  id: 'supplier-1',
  code: 'F000001',
  type: 'PJ' as const,
  name: 'Tech Distribuidora LTDA',
  document: '12345678000199',
  state_registration: null,
  municipal_registration: null,
  email: 'contato@techdistribuidora.test',
  phone: null,
  mobile: null,
  whatsapp: null,
  zipcode: null,
  street: null,
  number: null,
  district: null,
  city: 'Campinas',
  state: 'SP',
  country: 'Brasil',
  notes: null,
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

describe('suppliers store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps suppliers with pagination meta', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_SUPPLIER], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useSuppliersStore()

    await store.fetchSuppliers()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.city).toBe('Campinas')
    expect(store.meta.total).toBe(1)
    expect(store.error).toBeNull()
  })

  it('sends the current search term as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useSuppliersStore()
    store.setSearch('tech')

    await store.fetchSuppliers()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/suppliers',
      expect.objectContaining({ params: expect.objectContaining({ search: 'tech', page: 1 }) }),
    )
  })

  it('setSearch resets the page back to 1', () => {
    const store = useSuppliersStore()
    store.setPage(3)

    store.setSearch('nova busca')

    expect(store.page).toBe(1)
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useSuppliersStore()

    await store.fetchSuppliers()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createSupplier posts the snake_case payload and returns the mapped supplier', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SUPPLIER } })
    const store = useSuppliersStore()

    const created = await store.createSupplier({
      type: 'PJ',
      name: 'Tech Distribuidora LTDA',
      document: '12345678000199',
      email: 'contato@techdistribuidora.test',
    })

    expect(created?.code).toBe('F000001')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/suppliers',
      expect.objectContaining({
        type: 'PJ',
        name: 'Tech Distribuidora LTDA',
        document: '12345678000199',
      }),
    )
  })

  it('createSupplier returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(buildConflictError('Documento já cadastrado.'))
    const store = useSuppliersStore()

    const created = await store.createSupplier({
      type: 'PJ',
      name: 'Tech Distribuidora LTDA',
      document: '12345678000199',
    })

    expect(created).toBeNull()
    expect(store.error).toBe('Documento já cadastrado.')
  })

  it('updateSupplier patches the given id', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: RAW_SUPPLIER } })
    const store = useSuppliersStore()

    const updated = await store.updateSupplier('supplier-1', {
      type: 'PJ',
      name: 'Tech Distribuidora LTDA',
      phone: '19999999999',
    })

    expect(updated).not.toBeNull()
    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/suppliers/supplier-1',
      expect.objectContaining({ phone: '19999999999' }),
    )
  })

  it('deleteSupplier returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useSuppliersStore()

    const success = await store.deleteSupplier('supplier-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/suppliers/supplier-1')
  })

  it('deleteSupplier returns false and sets error on failure', async () => {
    vi.mocked(http.delete).mockRejectedValueOnce(new Error('network error'))
    const store = useSuppliersStore()

    const success = await store.deleteSupplier('supplier-1')

    expect(success).toBe(false)
    expect(store.error).not.toBeNull()
  })

  it('getSupplier returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useSuppliersStore()

    const supplier = await store.getSupplier('missing-id')

    expect(supplier).toBeNull()
  })
})
