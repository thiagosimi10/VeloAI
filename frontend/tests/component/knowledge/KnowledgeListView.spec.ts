import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import KnowledgeListView from '@/views/knowledge/KnowledgeListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_DOCUMENT = {
  id: 'document-1',
  title: 'Política de Garantia',
  content: 'Todo produto tem garantia de 90 dias contra defeitos de fabricação.',
  created_by: 'user-1',
  created_at: '2026-07-20T10:00:00Z',
  updated_at: '2026-07-20T10:00:00Z',
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function mountView() {
  return mount(KnowledgeListView, {
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('KnowledgeListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('renders the documents returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_DOCUMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Política de Garantia')
    expect(wrapper.text()).toContain('1 documento(s)')
  })

  it('shows an empty state message when there are no documents', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum documento cadastrado.')
  })

  it('creates a document and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const wrapper = mountView()
    await flushPromises()

    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_DOCUMENT } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_DOCUMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/knowledge', expect.any(Object))
    expect(wrapper.text()).toContain('Política de Garantia')
  })

  it('removes a document after confirmation', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_DOCUMENT], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const wrapper = mountView()
    await flushPromises()

    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    await wrapper.find('[aria-label="Remover Política de Garantia"]').trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/knowledge/document-1')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation(
      (_url: string, config?: { params?: { page?: number } }) => {
        const page = config?.params?.page ?? 1
        return Promise.resolve({
          data: { data: [RAW_DOCUMENT], meta: { page, page_size: 20, total: 25, pages: 2 } },
        }) as never
      },
    )

    const wrapper = mountView()
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/knowledge',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/knowledge',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
