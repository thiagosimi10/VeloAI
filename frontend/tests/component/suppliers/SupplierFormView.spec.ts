import { AxiosError, AxiosHeaders } from 'axios'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import SupplierFormView from '@/views/suppliers/SupplierFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_SUPPLIER = {
  id: 'supplier-1',
  code: 'F000001',
  type: 'PJ' as const,
  name: 'Tech Distribuidora LTDA',
  document: '12345678000199',
  state_registration: null,
  municipal_registration: null,
  email: 'contato@techdistribuidora.test',
  phone: '19999999999',
  mobile: null,
  whatsapp: null,
  zipcode: null,
  street: null,
  number: null,
  district: null,
  city: 'Campinas',
  state: 'SP',
  country: 'Brasil',
  notes: 'Fornecedor antigo.',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/suppliers', name: 'suppliers', component: { template: '<div />' } },
      { path: '/suppliers/new', name: 'suppliers-new', component: SupplierFormView },
      { path: '/suppliers/:id/edit', name: 'suppliers-edit', component: SupplierFormView },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(SupplierFormView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('SupplierFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('renders an empty create form', async () => {
    const router = buildRouter()
    router.push('/suppliers/new')
    await router.isReady()

    const wrapper = mountView(router)

    expect(wrapper.text()).toContain('Novo Fornecedor')
    expect((wrapper.find('#supplier-name').element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('#supplier-document').element as HTMLInputElement).disabled).toBe(false)
  })

  it('creates a supplier and redirects to the list on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SUPPLIER } })
    const router = buildRouter()
    router.push('/suppliers/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#supplier-document').setValue('12345678000199')
    await wrapper.find('#supplier-name').setValue('Tech Distribuidora LTDA')
    await wrapper.find('#supplier-email').setValue('contato@techdistribuidora.test')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/suppliers',
      expect.objectContaining({
        type: 'PF',
        name: 'Tech Distribuidora LTDA',
        document: '12345678000199',
        email: 'contato@techdistribuidora.test',
      }),
    )
    expect(router.currentRoute.value.name).toBe('suppliers')
  })

  it('shows an error message and stays on the page when creation fails', async () => {
    const error = new AxiosError('Conflict', '409', undefined, undefined, {
      status: 409,
      statusText: 'Conflict',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { message: 'Documento já cadastrado.' },
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const router = buildRouter()
    router.push('/suppliers/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#supplier-document').setValue('12345678000199')
    await wrapper.find('#supplier-name').setValue('Tech Distribuidora LTDA')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Documento já cadastrado.')
    expect(router.currentRoute.value.name).toBe('suppliers-new')
  })

  it('loads existing supplier data in edit mode and disables the document field', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUPPLIER } })
    const router = buildRouter()
    router.push('/suppliers/supplier-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Editar Fornecedor')
    expect((wrapper.find('#supplier-name').element as HTMLInputElement).value).toBe(
      'Tech Distribuidora LTDA',
    )
    expect((wrapper.find('#supplier-document').element as HTMLInputElement).value).toBe(
      '12345678000199',
    )
    expect((wrapper.find('#supplier-document').element as HTMLInputElement).disabled).toBe(true)
  })

  it('updates a supplier and redirects to the list on success', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_SUPPLIER } })
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_SUPPLIER, name: 'Tech Distribuidora Brasil LTDA' } },
    })
    const router = buildRouter()
    router.push('/suppliers/supplier-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('#supplier-name').setValue('Tech Distribuidora Brasil LTDA')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/suppliers/supplier-1',
      expect.objectContaining({ name: 'Tech Distribuidora Brasil LTDA' }),
    )
    expect(router.currentRoute.value.name).toBe('suppliers')
  })
})
