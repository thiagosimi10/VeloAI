import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AttachmentsPanel from '@/components/AttachmentsPanel.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_ATTACHMENT = {
  id: 'attachment-1',
  resource_type: 'service_order' as const,
  resource_id: 'order-1',
  original_filename: 'foto.jpg',
  content_type: 'image/jpeg',
  size_bytes: 2048,
  url: 'https://minio.test/presigned-url',
  uploaded_by: 'user-1',
  created_at: '2026-07-17T10:00:00Z',
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function mountPanel() {
  return mount(AttachmentsPanel, {
    props: { resourceType: 'service_order', resourceId: 'order-1' },
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('AttachmentsPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  it('renders the attachments returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [RAW_ATTACHMENT] } })

    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('foto.jpg')
    expect(wrapper.text()).toContain('2.0 KB')
  })

  it('shows an empty state message when there are no attachments', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [] } })

    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum anexo.')
  })

  it('uploads a file and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [] } })
    const wrapper = mountPanel()
    await flushPromises()

    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ATTACHMENT } })
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [RAW_ATTACHMENT] } })

    const file = new File(['fake-bytes'], 'foto.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('[data-testid="attachment-file-input"]')
      .element as HTMLInputElement
    Object.defineProperty(input, 'files', { value: [file] })
    await wrapper.find('[data-testid="attachment-file-input"]').trigger('change')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith('/api/v1/attachments', expect.any(FormData))
    expect(wrapper.text()).toContain('foto.jpg')
  })

  it('removes an attachment after confirmation', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [RAW_ATTACHMENT] } })
    const wrapper = mountPanel()
    await flushPromises()

    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: [] } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    await wrapper.find('[aria-label="Remover anexo"]').trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/attachments/attachment-1')
  })
})
