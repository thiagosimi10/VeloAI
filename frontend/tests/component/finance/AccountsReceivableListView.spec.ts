import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import AccountsReceivableListView from '@/views/finance/AccountsReceivableListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CUSTOMER = {
  id: 'customer-1',
  code: 'C000001',
  type: 'PF' as const,
  name: 'João Silva',
  document: '12345678901',
  state_registration: null,
  municipal_registration: null,
  email: null,
  phone: null,
  mobile: null,
  whatsapp: null,
  zipcode: null,
  street: null,
  number: null,
  district: null,
  city: null,
  state: null,
  country: 'Brasil',
  notes: null,
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_RECEIVABLE = {
  id: 'receivable-1',
  customer_id: 'customer-1',
  due_date: '2026-08-01',
  amount: '980.00',
  status: 'pending' as const,
  payment_date: null,
  is_overdue: false,
}

const EMPTY_CUSTOMERS_RESPONSE = {
  data: { data: [RAW_CUSTOMER], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accounts-receivable', name: 'accounts-receivable', component: AccountsReceivableListView },
      {
        path: '/accounts-receivable/new',
        name: 'accounts-receivable-new',
        component: { template: '<div />' },
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

describe('AccountsReceivableListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the receivables returned by the store with the resolved customer name', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
      if (url === '/api/v1/accounts-receivable') {
        return Promise.resolve({
          data: { data: [RAW_RECEIVABLE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-receivable')
    await router.isReady()

    const wrapper = mount(AccountsReceivableListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.text()).toContain('1 conta(s) a receber')
  })

  it('shows an empty state message when there are no receivables', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
      if (url === '/api/v1/accounts-receivable') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-receivable')
    await router.isReady()

    const wrapper = mount(AccountsReceivableListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhuma Conta a Receber encontrada.')
  })

  it('navigates to the new-receivable route when the button is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
      if (url === '/api/v1/accounts-receivable') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-receivable')
    await router.isReady()

    const wrapper = mount(AccountsReceivableListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-receivable-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('accounts-receivable-new')
  })

  it('navigates to the detail route when the view icon is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
      if (url === '/api/v1/accounts-receivable') {
        return Promise.resolve({
          data: { data: [RAW_RECEIVABLE], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/accounts-receivable')
    await router.isReady()

    const wrapper = mount(AccountsReceivableListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[aria-label="Ver conta a receber"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('accounts-receivable-detail')
    expect(router.currentRoute.value.params.id).toBe('receivable-1')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation(
      (url: string, config?: { params?: { page?: number } }) => {
        if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
        if (url === '/api/v1/accounts-receivable') {
          const page = config?.params?.page ?? 1
          return Promise.resolve({
            data: { data: [RAW_RECEIVABLE], meta: { page, page_size: 20, total: 25, pages: 2 } },
          }) as never
        }
        throw new Error(`unexpected GET ${url}`)
      },
    )
    const router = buildRouter()
    router.push('/accounts-receivable')
    await router.isReady()

    const wrapper = mount(AccountsReceivableListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/accounts-receivable',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/accounts-receivable',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
