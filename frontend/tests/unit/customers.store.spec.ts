import { AxiosError, AxiosHeaders } from 'axios'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useCustomersStore } from '@/stores/customers'

function buildConflictError(message: string): AxiosError {
  return new AxiosError('Conflict', '409', undefined, undefined, {
    status: 409,
    statusText: 'Conflict',
    headers: new AxiosHeaders(),
    config: { headers: new AxiosHeaders() },
    data: { message },
  } as never)
}

const RAW_CUSTOMER = {
  id: 'customer-1',
  code: 'C000001',
  type: 'PF' as const,
  name: 'João Silva',
  document: '12345678901',
  state_registration: null,
  municipal_registration: null,
  email: 'joao@empresa.test',
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

describe('customers store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps customers with pagination meta', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useCustomersStore()

    await store.fetchCustomers()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.city).toBe('Campinas')
    expect(store.meta.total).toBe(1)
    expect(store.error).toBeNull()
  })

  it('sends the current search term as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useCustomersStore()
    store.setSearch('joão')

    await store.fetchCustomers()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/customers',
      expect.objectContaining({ params: expect.objectContaining({ search: 'joão', page: 1 }) }),
    )
  })

  it('setSearch resets the page back to 1', () => {
    const store = useCustomersStore()
    store.setPage(3)

    store.setSearch('nova busca')

    expect(store.page).toBe(1)
  })

  it('sets a friendly error message when fetching fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('network error'))
    const store = useCustomersStore()

    await store.fetchCustomers()

    expect(store.error).toContain('Não foi possível')
    expect(store.items).toEqual([])
  })

  it('createCustomer posts the snake_case payload and returns the mapped customer', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_CUSTOMER } })
    const store = useCustomersStore()

    const created = await store.createCustomer({
      type: 'PF',
      name: 'João Silva',
      document: '12345678901',
      email: 'joao@empresa.test',
    })

    expect(created?.code).toBe('C000001')
    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/customers',
      expect.objectContaining({ type: 'PF', name: 'João Silva', document: '12345678901' }),
    )
  })

  it('createCustomer returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(buildConflictError('Documento já cadastrado.'))
    const store = useCustomersStore()

    const created = await store.createCustomer({
      type: 'PF',
      name: 'João Silva',
      document: '12345678901',
    })

    expect(created).toBeNull()
    expect(store.error).toBe('Documento já cadastrado.')
  })

  it('updateCustomer patches the given id', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: RAW_CUSTOMER } })
    const store = useCustomersStore()

    const updated = await store.updateCustomer('customer-1', {
      type: 'PF',
      name: 'João Silva',
      phone: '19999999999',
    })

    expect(updated).not.toBeNull()
    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/customers/customer-1',
      expect.objectContaining({ phone: '19999999999' }),
    )
  })

  it('deleteCustomer returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useCustomersStore()

    const success = await store.deleteCustomer('customer-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/customers/customer-1')
  })

  it('deleteCustomer returns false and sets error on failure', async () => {
    vi.mocked(http.delete).mockRejectedValueOnce(new Error('network error'))
    const store = useCustomersStore()

    const success = await store.deleteCustomer('customer-1')

    expect(success).toBe(false)
    expect(store.error).not.toBeNull()
  })

  it('getCustomer returns null when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('not found'))
    const store = useCustomersStore()

    const customer = await store.getCustomer('missing-id')

    expect(customer).toBeNull()
  })
})
