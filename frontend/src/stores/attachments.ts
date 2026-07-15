import { isAxiosError } from 'axios'
import { defineStore } from 'pinia'

import { http } from '@/services/http'

export type AttachmentResourceType = 'customer' | 'product' | 'service_order'

export interface Attachment {
  id: string
  resourceType: AttachmentResourceType
  resourceId: string
  originalFilename: string
  contentType: string
  sizeBytes: number
  url: string
  uploadedBy: string
  createdAt: string
}

interface RawAttachment {
  id: string
  resource_type: AttachmentResourceType
  resource_id: string
  original_filename: string
  content_type: string
  size_bytes: number
  url: string
  uploaded_by: string
  created_at: string
}

interface AttachmentsState {
  items: Attachment[]
  isLoading: boolean
  error: string | null
}

function mapAttachment(raw: RawAttachment): Attachment {
  return {
    id: raw.id,
    resourceType: raw.resource_type,
    resourceId: raw.resource_id,
    originalFilename: raw.original_filename,
    contentType: raw.content_type,
    sizeBytes: raw.size_bytes,
    url: raw.url,
    uploadedBy: raw.uploaded_by,
    createdAt: raw.created_at,
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

export const useAttachmentsStore = defineStore('attachments', {
  state: (): AttachmentsState => ({
    items: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchAttachments(
      resourceType: AttachmentResourceType,
      resourceId: string,
    ): Promise<void> {
      this.isLoading = true
      this.error = null

      try {
        const response = await http.get<{ data: RawAttachment[] }>('/api/v1/attachments', {
          params: { resource_type: resourceType, resource_id: resourceId },
        })
        this.items = response.data.data.map(mapAttachment)
      } catch (error) {
        this.error = extractErrorMessage(error)
      } finally {
        this.isLoading = false
      }
    },

    async uploadAttachment(
      resourceType: AttachmentResourceType,
      resourceId: string,
      file: File,
    ): Promise<Attachment | null> {
      this.error = null
      try {
        const formData = new FormData()
        formData.append('resource_type', resourceType)
        formData.append('resource_id', resourceId)
        formData.append('file', file)

        const response = await http.post<{ data: RawAttachment }>(
          '/api/v1/attachments',
          formData,
        )
        return mapAttachment(response.data.data)
      } catch (error) {
        this.error = extractErrorMessage(error)
        return null
      }
    },

    async deleteAttachment(id: string): Promise<boolean> {
      this.error = null
      try {
        await http.delete(`/api/v1/attachments/${id}`)
        return true
      } catch (error) {
        this.error = extractErrorMessage(error)
        return false
      }
    },
  },
})
