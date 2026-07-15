import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import CashFlowView from '@/views/finance/CashFlowView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_ENTRY = {
  id: 'entry-1',
  type: 'in' as const,
  category: 'Recebimento',
  description: 'Recebimento da Conta a Receber receivable-1',
  amount: '980.00',
  date: '2026-07-20',
  created_at: '2026-07-20T10:00:00Z',
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function mountView() {
  return mount(CashFlowView, {
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('CashFlowView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders the entries returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_ENTRY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Recebimento')
    expect(wrapper.text()).toContain('1 lançamento(s)')
  })

  it('shows an empty state message when there are no entries', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum lançamento encontrado.')
  })

  it('creates a manual entry and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const wrapper = mountView()
    await flushPromises()

    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ENTRY } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_ENTRY], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/cash-flow', expect.any(Object))
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation((_url: string, config?: { params?: { page?: number } }) => {
      const page = config?.params?.page ?? 1
      return Promise.resolve({
        data: { data: [RAW_ENTRY], meta: { page, page_size: 20, total: 25, pages: 2 } },
      }) as never
    })

    const wrapper = mountView()
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/cash-flow',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/cash-flow',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
