import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AccountReceivableFormView from '@/views/finance/AccountReceivableFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_CUSTOMERS_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}

const RAW_RECEIVABLE = {
  id: 'receivable-1',
  customer_id: '',
  due_date: '2026-08-01',
  amount: '980.00',
  status: 'pending' as const,
  payment_date: null,
  is_overdue: false,
}

function mockLookupFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accounts-receivable', name: 'accounts-receivable', component: { template: '<div />' } },
      {
        path: '/accounts-receivable/new',
        name: 'accounts-receivable-new',
        component: AccountReceivableFormView,
      },
      {
        path: '/accounts-receivable/:id',
        name: 'accounts-receivable-detail',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AccountReceivableFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders an empty create form', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/accounts-receivable/new')
    await router.isReady()

    const wrapper = mount(AccountReceivableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nova Conta a Receber')
    expect((wrapper.find('#receivable-due-date').element as HTMLInputElement).value).toBe('')
  })

  it('creates a receivable and redirects to the detail page on success', async () => {
    mockLookupFetches()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_RECEIVABLE } })
    const router = buildRouter()
    router.push('/accounts-receivable/new')
    await router.isReady()

    const wrapper = mount(AccountReceivableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('#receivable-due-date').setValue('2026-08-01')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/accounts-receivable',
      expect.objectContaining({ due_date: '2026-08-01' }),
    )
    expect(router.currentRoute.value.name).toBe('accounts-receivable-detail')
    expect(router.currentRoute.value.params.id).toBe('receivable-1')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/accounts-receivable/new')
    await router.isReady()

    const wrapper = mount(AccountReceivableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('accounts-receivable')
  })
})
