import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import SuppliersListView from '@/views/suppliers/SuppliersListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_SUPPLIER_1 = {
  id: 'supplier-1',
  code: 'F000001',
  type: 'PJ' as const,
  name: 'Tech Distribuidora LTDA',
  document: '12345678000199',
  state_registration: null,
  municipal_registration: null,
  email: 'contato@techdistribuidora.test',
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

const RAW_SUPPLIER_2 = {
  ...RAW_SUPPLIER_1,
  id: 'supplier-2',
  code: 'F000002',
  name: 'Componentes Brasil LTDA',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/suppliers', name: 'suppliers', component: SuppliersListView },
      { path: '/suppliers/new', name: 'suppliers-new', component: { template: '<div />' } },
      {
        path: '/suppliers/:id/edit',
        name: 'suppliers-edit',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('SuppliersListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the suppliers returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: {
        data: [RAW_SUPPLIER_1, RAW_SUPPLIER_2],
        meta: { page: 1, page_size: 20, total: 2, pages: 1 },
      },
    })
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Tech Distribuidora LTDA')
    expect(wrapper.text()).toContain('Componentes Brasil LTDA')
    expect(wrapper.text()).toContain('2 fornecedor(es)')
  })

  it('shows an empty state message when there are no suppliers', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum fornecedor encontrado.')
  })

  it('triggers a new search when the search form is submitted', async () => {
    vi.mocked(http.get).mockResolvedValue({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('input').setValue('tech')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/suppliers',
      expect.objectContaining({ params: expect.objectContaining({ search: 'tech' }) }),
    )
  })

  it('navigates to the new-supplier route when the button is clicked', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-supplier-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('suppliers-new')
  })

  it('deletes a supplier after confirmation and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_SUPPLIER_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_SUPPLIER_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/suppliers/supplier-1')
    expect(http.get).toHaveBeenCalledTimes(2)
  })

  it('does not delete when the confirmation dialog is dismissed', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_SUPPLIER_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    const router = buildRouter()
    router.push('/suppliers')
    await router.isReady()

    const wrapper = mount(SuppliersListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_SUPPLIER_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).not.toHaveBeenCalled()
  })
})
