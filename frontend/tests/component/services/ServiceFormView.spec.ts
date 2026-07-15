import { AxiosError, AxiosHeaders } from 'axios'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ServiceFormView from '@/views/services/ServiceFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_CATEGORY_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}

const RAW_SERVICE = {
  id: 'service-1',
  category_id: null,
  code: 'S000001',
  name: 'Formatação de Computador',
  description: null,
  estimated_time: 60,
  price: '180.00',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function mockCategoriesFetch(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/services', name: 'services', component: { template: '<div />' } },
      { path: '/services/new', name: 'services-new', component: ServiceFormView },
      { path: '/services/:id/edit', name: 'services-edit', component: ServiceFormView },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(ServiceFormView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ServiceFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('renders an empty create form', async () => {
    mockCategoriesFetch()
    const router = buildRouter()
    router.push('/services/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    expect(wrapper.text()).toContain('Novo Serviço')
    expect((wrapper.find('#service-name').element as HTMLInputElement).value).toBe('')
  })

  it('creates a service and redirects to the list on success', async () => {
    mockCategoriesFetch()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_SERVICE } })
    const router = buildRouter()
    router.push('/services/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('#service-name').setValue('Formatação de Computador')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/services',
      expect.objectContaining({ name: 'Formatação de Computador' }),
    )
    expect(router.currentRoute.value.name).toBe('services')
  })

  it('shows an error message and stays on the page when creation fails', async () => {
    mockCategoriesFetch()
    const error = new AxiosError('Conflict', '409', undefined, undefined, {
      status: 409,
      statusText: 'Conflict',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { message: 'Categoria não encontrada.' },
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const router = buildRouter()
    router.push('/services/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('#service-name').setValue('Formatação de Computador')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Categoria não encontrada.')
    expect(router.currentRoute.value.name).toBe('services-new')
  })

  it('loads existing service data in edit mode', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services/service-1') {
        return Promise.resolve({ data: { data: RAW_SERVICE } }) as never
      }
      return Promise.reject(new Error(`unexpected GET ${url}`)) as never
    })
    const router = buildRouter()
    router.push('/services/service-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Editar Serviço')
    expect((wrapper.find('#service-name').element as HTMLInputElement).value).toBe(
      'Formatação de Computador',
    )
  })

  it('updates a service and redirects to the list on success', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services/service-1') {
        return Promise.resolve({ data: { data: RAW_SERVICE } }) as never
      }
      return Promise.reject(new Error(`unexpected GET ${url}`)) as never
    })
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_SERVICE, name: 'Formatação Completa' } },
    })
    const router = buildRouter()
    router.push('/services/service-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('#service-name').setValue('Formatação Completa')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/services/service-1',
      expect.objectContaining({ name: 'Formatação Completa' }),
    )
    expect(router.currentRoute.value.name).toBe('services')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockCategoriesFetch()
    const router = buildRouter()
    router.push('/services/new')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('services')
  })
})
