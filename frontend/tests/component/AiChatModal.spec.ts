import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AiChatModal from '@/components/AiChatModal.vue'
import { VeloAIPreset } from '@/plugins/primevue-theme'
import { useAiStore } from '@/stores/ai'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

function mountModal() {
  return mount(AiChatModal, {
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('AiChatModal', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('is hidden by default', () => {
    const wrapper = mountModal()

    expect(wrapper.find('[data-testid="ai-chat-modal"]').exists()).toBe(false)
  })

  it('shows the AI assistant panel when the store opens the chat', async () => {
    const store = useAiStore()
    store.openChat()
    const wrapper = mountModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-testid="ai-chat-modal"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="ai-assistant-prompt"]').exists()).toBe(true)
  })

  it('closes the chat when the close button is clicked', async () => {
    const store = useAiStore()
    store.openChat()
    const wrapper = mountModal()
    await wrapper.vm.$nextTick()

    await wrapper.find('[data-testid="ai-chat-close-button"]').trigger('click')

    expect(store.isChatOpen).toBe(false)
  })
})
