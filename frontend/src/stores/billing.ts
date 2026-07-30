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

export interface PlanTier {
  cycle: string
  label: string
  months: number
  monthlyPrice: string
  totalPrice: string
}

interface RawPlanTier {
  cycle: string
  label: string
  months: number
  monthly_price: string
  total_price: string
}

interface BillingState {
  subscription: Subscription | null
  planTiers: PlanTier[]
  isLoading: boolean
  isCheckingOut: boolean
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

function mapPlanTier(raw: RawPlanTier): PlanTier {
  return {
    cycle: raw.cycle,
    label: raw.label,
    months: raw.months,
    monthlyPrice: raw.monthly_price,
    totalPrice: raw.total_price,
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
    planTiers: [],
    isLoading: false,
    isCheckingOut: false,
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

    async fetchPlanTiers(): Promise<void> {
      this.error = null

      try {
        const response = await http.get<{ data: RawPlanTier[] }>('/api/v1/billing/plans')
        this.planTiers = response.data.data.map(mapPlanTier)
      } catch (error) {
        this.error = extractErrorMessage(error)
      }
    },

    /** Mesmos dados de `fetchPlanTiers`, mas sem exigir sessão — usado pelas páginas
     * públicas de marketing, que nunca devem mostrar um preço diferente do checkout. */
    async fetchPublicPlanTiers(): Promise<void> {
      this.error = null

      try {
        const response = await http.get<{ data: RawPlanTier[] }>('/api/v1/billing/public/plans')
        this.planTiers = response.data.data.map(mapPlanTier)
      } catch (error) {
        this.error = extractErrorMessage(error)
      }
    },

    async createCheckout(cycle: string): Promise<string | null> {
      this.isCheckingOut = true
      this.error = null

      try {
        const response = await http.post<{ data: { checkout_url: string } }>(
          '/api/v1/billing/checkout',
          { cycle },
        )
        return response.data.data.checkout_url
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      } finally {
        this.isCheckingOut = false
      }
    },
  },
})
