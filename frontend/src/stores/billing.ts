import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface Subscription {
  planName: string
  planPrice: string
  status: string
  trialEndsAt: string | null
  currentPeriodEndsAt: string | null
  daysRemaining: number | null
}

interface RawSubscription {
  plan_name: string
  plan_price: string
  status: string
  trial_ends_at: string | null
  current_period_ends_at: string | null
  days_remaining: number | null
}

interface BillingState {
  subscription: Subscription | null
  isLoading: boolean
  error: string | null
}

function mapSubscription(raw: RawSubscription): Subscription {
  return {
    planName: raw.plan_name,
    planPrice: raw.plan_price,
    status: raw.status,
    trialEndsAt: raw.trial_ends_at,
    currentPeriodEndsAt: raw.current_period_ends_at,
    daysRemaining: raw.days_remaining,
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

export const useBillingStore = defineStore('billing', {
  state: (): BillingState => ({
    subscription: null,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSubscription(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawSubscription }>('/api/v1/billing/subscription')
        this.subscription = mapSubscription(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async cancelSubscription(): Promise<boolean> {
      this.error = null

      try {
        const response = await http.post<{ data: RawSubscription }>('/api/v1/billing/cancel')
        this.subscription = mapSubscription(response.data.data)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
