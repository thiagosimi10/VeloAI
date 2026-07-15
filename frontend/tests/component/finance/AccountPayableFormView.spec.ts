import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AccountPayableFormView from '@/views/finance/AccountPayableFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_SUPPLIERS_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}

const RAW_PAYABLE = {
  id: 'payable-1',
  supplier_id: '',
  due_date: '2026-08-01',
  amount: '320.00',
  status: 'pending' as const,
  payment_date: null,
  is_overdue: false,
}

function mockLookupFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/suppliers') return Promise.resolve(EMPTY_SUPPLIERS_RESPONSE) as never
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accounts-payable', name: 'accounts-payable', component: { template: '<div />' } },
      {
        path: '/accounts-payable/new',
        name: 'accounts-payable-new',
        component: AccountPayableFormView,
      },
      {
        path: '/accounts-payable/:id',
        name: 'accounts-payable-detail',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AccountPayableFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders an empty create form', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/accounts-payable/new')
    await router.isReady()

    const wrapper = mount(AccountPayableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nova Conta a Pagar')
    expect((wrapper.find('#payable-due-date').element as HTMLInputElement).value).toBe('')
  })

  it('creates a payable and redirects to the detail page on success', async () => {
    mockLookupFetches()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_PAYABLE } })
    const router = buildRouter()
    router.push('/accounts-payable/new')
    await router.isReady()

    const wrapper = mount(AccountPayableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('#payable-due-date').setValue('2026-08-01')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/accounts-payable',
      expect.objectContaining({ due_date: '2026-08-01' }),
    )
    expect(router.currentRoute.value.name).toBe('accounts-payable-detail')
    expect(router.currentRoute.value.params.id).toBe('payable-1')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/accounts-payable/new')
    await router.isReady()

    const wrapper = mount(AccountPayableFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('accounts-payable')
  })
})
