import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import BillingView from '@/views/BillingView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_SUBSCRIPTION = {
  plan_name: 'VeloAI Professional',
  plan_price: '129.90',
  status: 'TRIAL',
  trial_ends_at: '2026-08-01T00:00:00Z',
  current_period_ends_at: null,
  days_remaining: 5,
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function mountView() {
  return mount(BillingView, {
    global: { plugins: [[PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

describe('BillingView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders the plan, status and trial days remaining', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUBSCRIPTION } })
    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('VeloAI Professional')
    expect(wrapper.text()).toContain('Período de Teste')
    expect(wrapper.text()).toContain('R$')
    expect(wrapper.find('[data-testid="subscription-status"]').text()).toContain(
      'Período de Teste',
    )
  })

  it('cancels the subscription when confirmed', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUBSCRIPTION } })
    vi.mocked(http.post).mockResolvedValueOnce({
      data: { data: { ...RAW_SUBSCRIPTION, status: 'CANCELED' } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('[data-testid="cancel-subscription-button"]').trigger('click')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(http.post).toHaveBeenCalledWith('/api/v1/billing/cancel')
    expect(wrapper.find('[data-testid="subscription-status"]').text()).toContain('Cancelada')
  })

  it('does not cancel when the confirmation is declined', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUBSCRIPTION } })
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('[data-testid="cancel-subscription-button"]').trigger('click')

    expect(http.post).not.toHaveBeenCalled()
  })

  it('shows an error message when the request fails', async () => {
    vi.mocked(http.get).mockRejectedValueOnce(new Error('failed'))
    const wrapper = mountView()
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Não foi possível concluir a operação')
  })
})
