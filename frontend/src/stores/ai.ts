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
  toolUsed: string | null
}

interface RawAskAIResponse {
  response: string
  model: string
  tokens: number
  execution_time: string
  cached: boolean
  estimated_cost: string
  tool_used: string | null
}

interface AiState {
  isLoading: boolean
  error: string | null
  lastResult: AskAIResult | null
  isChatOpen: boolean
}

function mapAskAIResponse(raw: RawAskAIResponse): AskAIResult {
  return {
    response: raw.response,
    model: raw.model,
    tokens: raw.tokens,
    executionTime: raw.execution_time,
    cached: raw.cached,
    estimatedCost: raw.estimated_cost,
    toolUsed: raw.tool_used,
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
    isChatOpen: false,
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
    openChat(): void {
      this.isChatOpen = true
    },
    closeChat(): void {
      this.isChatOpen = false
    },
    toggleChat(): void {
      this.isChatOpen = !this.isChatOpen
    },
  },
})
