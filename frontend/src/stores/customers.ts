import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type CustomerType = 'PF' | 'PJ'

export interface Customer {
  id: string
  code: string
  type: CustomerType
  name: string
  document: string
  stateRegistration: string | null
  municipalRegistration: string | null
  email: string | null
  phone: string | null
  mobile: string | null
  whatsapp: string | null
  zipcode: string | null
  street: string | null
  number: string | null
  district: string | null
  city: string | null
  state: string | null
  country: string
  notes: string | null
  active: boolean
  createdAt: string
  updatedAt: string
}

export interface CustomerFormPayload {
  type: CustomerType
  name: string
  document?: string
  stateRegistration?: string | null
  municipalRegistration?: string | null
  email?: string | null
  phone?: string | null
  mobile?: string | null
  whatsapp?: string | null
  zipcode?: string | null
  street?: string | null
  number?: string | null
  district?: string | null
  city?: string | null
  state?: string | null
  country?: string
  notes?: string | null
}

interface RawCustomer {
  id: string
  code: string
  type: CustomerType
  name: string
  document: string
  state_registration: string | null
  municipal_registration: string | null
  email: string | null
  phone: string | null
  mobile: string | null
  whatsapp: string | null
  zipcode: string | null
  street: string | null
  number: string | null
  district: string | null
  city: string | null
  state: string | null
  country: string
  notes: string | null
  active: boolean
  created_at: string
  updated_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface CustomersState {
  items: Customer[]
  meta: PaginationMeta
  search: string
  page: number
  isLoading: boolean
  error: string | null
}

function mapCustomer(raw: RawCustomer): Customer {
  return {
    id: raw.id,
    code: raw.code,
    type: raw.type,
    name: raw.name,
    document: raw.document,
    stateRegistration: raw.state_registration,
    municipalRegistration: raw.municipal_registration,
    email: raw.email,
    phone: raw.phone,
    mobile: raw.mobile,
    whatsapp: raw.whatsapp,
    zipcode: raw.zipcode,
    street: raw.street,
    number: raw.number,
    district: raw.district,
    city: raw.city,
    state: raw.state,
    country: raw.country,
    notes: raw.notes,
    active: raw.active,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  }
}

function toRawPayload(payload: CustomerFormPayload): Record<string, unknown> {
  return {
    type: payload.type,
    name: payload.name,
    document: payload.document,
    state_registration: payload.stateRegistration,
    municipal_registration: payload.municipalRegistration,
    email: payload.email || null,
    phone: payload.phone,
    mobile: payload.mobile,
    whatsapp: payload.whatsapp,
    zipcode: payload.zipcode,
    street: payload.street,
    number: payload.number,
    district: payload.district,
    city: payload.city,
    state: payload.state,
    country: payload.country,
    notes: payload.notes,
  }
}

function extractErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const message = (error.response?.data as { message?: unknown } | undefined)?.message
    if (typeof message === 'string') {
      return message
    }
  }
  return 'Não foi possível concluir a operação. Tente novamente.'
}

export const useCustomersStore = defineStore('customers', {
  state: (): CustomersState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    search: '',
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCustomers(options: { pageSize?: number } = {}): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawCustomer[]; meta: PaginationMeta }>(
          '/api/v1/customers',
          {
            params: {
              search: this.search || undefined,
              page: this.page,
              page_size: options.pageSize,
            },
          },
        )
        this.items = response.data.data.map(mapCustomer)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    setSearch(value: string): void {
      this.search = value
      this.page = 1
    },

    setPage(value: number): void {
      this.page = value
    },

    async getCustomer(id: string): Promise<Customer | null> {
      try {
        const response = await http.get<{ data: RawCustomer }>(`/api/v1/customers/${id}`)
        return mapCustomer(response.data.data)
      } catch {
        return null
      }
    },

    async createCustomer(payload: CustomerFormPayload): Promise<Customer | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawCustomer }>(
          '/api/v1/customers',
          toRawPayload(payload),
        )
        return mapCustomer(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async updateCustomer(id: string, payload: CustomerFormPayload): Promise<Customer | null> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawCustomer }>(
          `/api/v1/customers/${id}`,
          toRawPayload(payload),
        )
        return mapCustomer(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteCustomer(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/customers/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
