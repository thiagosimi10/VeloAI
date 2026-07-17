import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'
import { useKnowledgeStore } from '@/stores/knowledge'

const RAW_DOCUMENT = {
  id: 'document-1',
  title: 'Política de Garantia',
  content: 'Todo produto tem garantia de 90 dias contra defeitos de fabricação.',
  created_by: 'user-1',
  created_at: '2026-07-20T10:00:00Z',
  updated_at: '2026-07-20T10:00:00Z',
}

describe('knowledge store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('fetches and maps documents', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_DOCUMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const store = useKnowledgeStore()

    await store.fetchDocuments()

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.title).toBe('Política de Garantia')
    expect(store.error).toBeNull()
  })

  it('fetchDocuments sends the current page as a query param', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 2, page_size: 20, total: 0, pages: 0 } },
    })
    const store = useKnowledgeStore()
    store.setPage(2)

    await store.fetchDocuments()

    expect(http.get).toHaveBeenCalledWith(
      '/api/v1/knowledge',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )
  })

  it('createDocument posts the payload and returns the mapped document', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_DOCUMENT } })
    const store = useKnowledgeStore()

    const created = await store.createDocument({
      title: 'Política de Garantia',
      content: 'Todo produto tem garantia de 90 dias contra defeitos de fabricação.',
    })

    expect(created?.title).toBe('Política de Garantia')
    expect(http.post).toHaveBeenCalledWith('/api/v1/knowledge', {
      title: 'Política de Garantia',
      content: 'Todo produto tem garantia de 90 dias contra defeitos de fabricação.',
    })
  })

  it('createDocument returns null and sets error on failure', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const store = useKnowledgeStore()

    const result = await store.createDocument({ title: 'Título', content: 'Conteúdo' })

    expect(result).toBeNull()
    expect(store.error).not.toBeNull()
  })

  it('deleteDocument returns true on success', async () => {
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    const store = useKnowledgeStore()

    const success = await store.deleteDocument('document-1')

    expect(success).toBe(true)
    expect(http.delete).toHaveBeenCalledWith('/api/v1/knowledge/document-1')
  })

  it('deleteDocument returns false and sets error on failure', async () => {
    vi.mocked(http.delete).mockRejectedValueOnce(new Error('failed'))
    const store = useKnowledgeStore()

    const success = await store.deleteDocument('document-1')

    expect(success).toBe(false)
    expect(store.error).not.toBeNull()
  })
})
