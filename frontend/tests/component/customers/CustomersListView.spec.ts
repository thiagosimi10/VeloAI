import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import CustomersListView from '@/views/customers/CustomersListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CUSTOMER_1 = {
  id: 'customer-1',
  code: 'C000001',
  type: 'PF' as const,
  name: 'João Silva',
  document: '12345678901',
  state_registration: null,
  municipal_registration: null,
  email: 'joao@empresa.test',
  phone: null,
  mobile: null,
  whatsapp: null,
  zipcode: null,
  street: null,
  number: null,
  district: null,
  city: 'Campinas',
  state: 'SP',
  country: 'Brasil',
  notes: null,
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_CUSTOMER_2 = { ...RAW_CUSTOMER_1, id: 'customer-2', code: 'C000002', name: 'Maria Souza' }

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers', name: 'customers', component: CustomersListView },
      { path: '/customers/new', name: 'customers-new', component: { template: '<div />' } },
      {
        path: '/customers/:id/edit',
        name: 'customers-edit',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('CustomersListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the customers returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: {
        data: [RAW_CUSTOMER_1, RAW_CUSTOMER_2],
        meta: { page: 1, page_size: 20, total: 2, pages: 1 },
      },
    })
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.text()).toContain('Maria Souza')
    expect(wrapper.text()).toContain('2 cliente(s)')
  })

  it('shows an empty state message when there are no customers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum cliente encontrado.')
  })

  it('triggers a new search when the search form is submitted', async () => {
    vi.mocked(http.get).mockResolvedValue({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('input').setValue('joão')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/customers',
      expect.objectContaining({ params: expect.objectContaining({ search: 'joão' }) }),
    )
  })

  it('navigates to the new-customer route when the button is clicked', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-customer-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('customers-new')
  })

  it('deletes a customer after confirmation and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CUSTOMER_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_CUSTOMER_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/customers/customer-1')
    expect(http.get).toHaveBeenCalledTimes(2)
  })

  it('does not delete when the confirmation dialog is dismissed', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CUSTOMER_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const router = buildRouter()
    router.push('/customers')
    await router.isReady()

    const wrapper = mount(CustomersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_CUSTOMER_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).not.toHaveBeenCalled()
  })
})
