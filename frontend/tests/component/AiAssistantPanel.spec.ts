import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import AiAssistantPanel from '@/components/AiAssistantPanel.vue'
import { VeloAIPreset } from '@/plugins/primevue-theme'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_ASK_AI_RESPONSE = {
  response: 'Você vendeu R$ 12.340,00 em maio.',
  model: 'gemini-3.1-flash-lite',
  tokens: 60,
  execution_time: '1.234',
  cached: false,
  estimated_cost: '0.0000120',
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function mountPanel() {
  return mount(AiAssistantPanel, {
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('AiAssistantPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.post).mockReset()
  })

  it('asks the AI assistant and renders the response', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ASK_AI_RESPONSE } })
    const wrapper = mountPanel()

    await wrapper.find('[data-testid="ai-assistant-prompt"]').setValue('Quanto vendi em maio?')
    await wrapper.find('[data-testid="ai-assistant-ask-button"]').trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(http.post).toHaveBeenCalledWith('/api/v1/ai/ask', { prompt: 'Quanto vendi em maio?' })
    expect(wrapper.text()).toContain('Você vendeu R$ 12.340,00 em maio.')
    expect(wrapper.text()).toContain('gemini-3.1-flash-lite')
  })

  it('shows an error message when the request fails', async () => {
    vi.mocked(http.post).mockRejectedValueOnce(new Error('failed'))
    const wrapper = mountPanel()

    await wrapper.find('[data-testid="ai-assistant-prompt"]').setValue('Quanto vendi em maio?')
    await wrapper.find('[data-testid="ai-assistant-ask-button"]').trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Não foi possível concluir a operação')
  })
})
