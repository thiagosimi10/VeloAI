import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface Company {
  id: string
  legalName: string
  tradeName: string | null
  document: string
  email: string | null
  phone: string | null
  timezone: string
  currency: string
}

export interface CompanyFormPayload {
  legalName: string
  tradeName?: string | null
  email?: string | null
  phone?: string | null
}

interface RawCompany {
  id: string
  legal_name: string
  trade_name: string | null
  document: string
  email: string | null
  phone: string | null
  timezone: string
  currency: string
}

interface CompanyState {
  company: Company | null
  isLoading: boolean
  error: string | null
}

function mapCompany(raw: RawCompany): Company {
  return {
    id: raw.id,
    legalName: raw.legal_name,
    tradeName: raw.trade_name,
    document: raw.document,
    email: raw.email,
    phone: raw.phone,
    timezone: raw.timezone,
    currency: raw.currency,
  }
}

function toRawPayload(payload: CompanyFormPayload): Record<string, unknown> {
  return {
    legal_name: payload.legalName,
    trade_name: payload.tradeName || null,
    email: payload.email || null,
    phone: payload.phone || null,
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

export const useCompanyStore = defineStore('company', {
  state: (): CompanyState => ({
    company: null,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCompany(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawCompany }>('/api/v1/company')
        this.company = mapCompany(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async updateCompany(payload: CompanyFormPayload): Promise<boolean> {
      this.error = null
      try {
        const response = await http.patch<{ data: RawCompany }>(
          '/api/v1/company',
          toRawPayload(payload),
        )
        this.company = mapCompany(response.data.data)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
