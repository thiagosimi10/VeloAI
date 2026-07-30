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

export interface AttachedFile {
  uploadId: string
  filename: string
  rowCount: number
  headers: string[]
}

interface RawAiUploadResponse {
  upload_id: string
  filename: string
  row_count: number
  headers: string[]
}

interface AiState {
  isLoading: boolean
  isUploading: boolean
  error: string | null
  lastResult: AskAIResult | null
  isChatOpen: boolean
  attachedFile: AttachedFile | null
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
    isUploading: false,
    error: null,
    lastResult: null,
    isChatOpen: false,
    attachedFile: null,
  }),
  actions: {
    async askAI(prompt: string): Promise<AskAIResult | null> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.post<{ data: RawAskAIResponse }>('/api/v1/ai/ask', {
          prompt,
          upload_id: this.attachedFile?.uploadId ?? null,
        })
        this.lastResult = mapAskAIResponse(response.data.data)
        this.attachedFile = null
        return this.lastResult
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      } finally {
        this.isLoading = false
      }
    },
    async uploadFile(file: File): Promise<boolean> {
      this.isUploading = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await http.post<{ data: RawAiUploadResponse }>(
          '/api/v1/ai/uploads',
          formData,
        )
        const raw = response.data.data
        this.attachedFile = {
          uploadId: raw.upload_id,
          filename: raw.filename,
          rowCount: raw.row_count,
          headers: raw.headers,
        }
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      } finally {
        this.isUploading = false
      }
    },
    clearAttachedFile(): void {
      this.attachedFile = null
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
