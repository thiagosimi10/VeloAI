import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useAttachmentsStore } from '@/stores/attachments'

const RAW_ATTACHMENT = {
  id: 'attachment-1',
  resource_type: 'service_order' as const,
  resource_id: 'order-1',
  original_filename: 'foto.jpg',
  content_type: 'image/jpeg',
  size_bytes: 1024,
  url: 'https://minio.test/presigned-url',
  uploaded_by: 'user-1',
  created_at: '2026-07-17T10:00:00Z',
}

describe('attachments store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps attachments for a resource', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [RAW_ATTACHMENT] } })
    const store = useAttachmentsStore()

    await store.fetchAttachments('service_order', 'order-1')

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.originalFilename).toBe('foto.jpg')
    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/attachments',
      expect.objectContaining({
        params: { resource_type: 'service_order', resource_id: 'order-1' },
      }),
    )
  })

  it('uploadAttachment sends a FormData payload and returns the mapped attachment', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ATTACHMENT } })
    const store = useAttachmentsStore()
    const file = new File(['fake-bytes'], 'foto.jpg', { type: 'image/jpeg' })

    const result = await store.uploadAttachment('service_order', 'order-1', file)

    expect(result?.originalFilename).toBe('foto.jpg')
    const [url, formData] = vi.mocked(http.post).mock.calls[0] ?? []
    expect(url).toBe('/api/v1/attachments')
    expect(formData).toBeInstanceOf(FormData)
    expect((formData as FormData).get('resource_type')).toBe('service_order')
    expect((formData as FormData).get('resource_id')).toBe('order-1')
    expect((formData as FormData).get('file')).toBe(file)
  })

  it('uploadAttachment returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useAttachmentsStore()
    const file = new File(['fake-bytes'], 'foto.jpg', { type: 'image/jpeg' })

    const result = await store.uploadAttachment('service_order', 'order-1', file)

    expect(result).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('deleteAttachment returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useAttachmentsStore()

    const success = await store.deleteAttachment('attachment-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/attachments/attachment-1')
  })
})
