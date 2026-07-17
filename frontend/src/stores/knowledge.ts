import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export interface KnowledgeDocument {
  id: string
  title: string
  content: string
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface CreateKnowledgeDocumentPayload {
  title: string
  content: string
}

interface RawKnowledgeDocument {
  id: string
  title: string
  content: string
  created_by: string
  created_at: string
  updated_at: string
}

interface PaginationMeta {
  page: number
  page_size: number
  total: number
  pages: number
}

interface KnowledgeState {
  items: KnowledgeDocument[]
  meta: PaginationMeta
  page: number
  isLoading: boolean
  error: string | null
}

function mapDocument(raw: RawKnowledgeDocument): KnowledgeDocument {
  return {
    id: raw.id,
    title: raw.title,
    content: raw.content,
    createdBy: raw.created_by,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
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

export const useKnowledgeStore = defineStore('knowledge', {
  state: (): KnowledgeState => ({
    items: [],
    meta: { page: 1, page_size: 20, total: 0, pages: 0 },
    page: 1,
    isLoading: false,
    error: null,
  }),
  actions: {
    setPage(value: number): void {
      this.page = value
    },

    async fetchDocuments(): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawKnowledgeDocument[]; meta: PaginationMeta }>(
          '/api/v1/knowledge',
          { params: { page: this.page } },
        )
        this.items = response.data.data.map(mapDocument)
        this.meta = response.data.meta
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async createDocument(
      payload: CreateKnowledgeDocumentPayload,
    ): Promise<KnowledgeDocument | null> {
      this.error = null
      try {
        const response = await http.post<{ data: RawKnowledgeDocument }>(
          '/api/v1/knowledge',
          payload,
        )
        return mapDocument(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteDocument(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/knowledge/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
