import { AxiosError, AxiosHeaders } from 'axios'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import CustomerFormView from '@/views/customers/CustomerFormView.vue'

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
  email: 'joao@empresa.test',
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
  notes: 'Cliente antigo.',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers', name: 'customers', component: { template: '<div />' } },
      { path: '/customers/new', name: 'customers-new', component: CustomerFormView },
      { path: '/customers/:id/edit', name: 'customers-edit', component: CustomerFormView },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(CustomerFormView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('CustomerFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('renders an empty create form', async () => {
    const router = buildRouter()
    router.push('/customers/new')
    await router.isReady()

    const wrapper = mountView(router)

    expect(wrapper.text()).toContain('Novo Cliente')
    expect((wrapper.find('#customer-name').element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('#customer-document').element as HTMLInputElement).disabled).toBe(false)
  })

  it('creates a customer and redirects to the list on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_CUSTOMER } })
    const router = buildRouter()
    router.push('/customers/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#customer-document').setValue('12345678901')
    await wrapper.find('#customer-name').setValue('João Silva')
    await wrapper.find('#customer-email').setValue('joao@empresa.test')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/customers',
      expect.objectContaining({
        type: 'PF',
        name: 'João Silva',
        document: '12345678901',
        email: 'joao@empresa.test',
      }),
    )
    expect(router.currentRoute.value.name).toBe('customers')
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
    router.push('/customers/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#customer-document').setValue('12345678901')
    await wrapper.find('#customer-name').setValue('João Silva')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Documento já cadastrado.')
    expect(router.currentRoute.value.name).toBe('customers-new')
  })

  it('loads existing customer data in edit mode and disables the document field', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_CUSTOMER } })
    const router = buildRouter()
    router.push('/customers/customer-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Editar Cliente')
    expect((wrapper.find('#customer-name').element as HTMLInputElement).value).toBe('João Silva')
    expect((wrapper.find('#customer-document').element as HTMLInputElement).value).toBe(
      '12345678901',
    )
    expect((wrapper.find('#customer-document').element as HTMLInputElement).disabled).toBe(true)
  })

  it('updates a customer and redirects to the list on success', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_CUSTOMER } })
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_CUSTOMER, name: 'João S. Silva' } },
    })
    const router = buildRouter()
    router.push('/customers/customer-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('#customer-name').setValue('João S. Silva')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/customers/customer-1',
      expect.objectContaining({ name: 'João S. Silva' }),
    )
    expect(router.currentRoute.value.name).toBe('customers')
  })
})
