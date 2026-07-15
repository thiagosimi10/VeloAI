import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface AskAIResult {
  response: string
  model: string
  tokens: number
  executionTime: string
  cached: boolean
  estimatedCost: string
}

interface RawAskAIResponse {
  response: string
  model: string
  tokens: number
  execution_time: string
  cached: boolean
  estimated_cost: string
}

interface AiState {
  isLoading: boolean
  error: string | null
  lastResult: AskAIResult | null
}

function mapAskAIResponse(raw: RawAskAIResponse): AskAIResult {
  return {
    response: raw.response,
    model: raw.model,
    tokens: raw.tokens,
    executionTime: raw.execution_time,
    cached: raw.cached,
    estimatedCost: raw.estimated_cost,
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

export const useAiStore = defineStore('ai', {
  state: (): AiState => ({
    isLoading: false,
    error: null,
    lastResult: null,
  }),
  actions: {
    async askAI(prompt: string): Promise<AskAIResult | null> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: RawAskAIResponse }>('/api/v1/ai/ask', { prompt })
        this.lastResult = mapAskAIResponse(response.data.data)
        return this.lastResult
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      } finally {
        this.isLoading = false
      }
    },
  },
})
