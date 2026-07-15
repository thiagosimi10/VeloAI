import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ServicesListView from '@/views/services/ServicesListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CATEGORY = {
  id: 'category-1',
  name: 'Manutenção',
  description: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_SERVICE_1 = {
  id: 'service-1',
  category_id: 'category-1',
  code: 'S000001',
  name: 'Formatação de Computador',
  description: null,
  estimated_time: 60,
  price: '180.00',
  active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_SERVICE_2 = { ...RAW_SERVICE_1, id: 'service-2', code: 'S000002', name: 'Diagnóstico' }

const EMPTY_CATEGORY_RESPONSE = {
  data: { data: [RAW_CATEGORY], meta: { page: 1, page_size: 100, total: 1, pages: 1 } },
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/services', name: 'services', component: ServicesListView },
      { path: '/services/new', name: 'services-new', component: { template: '<div />' } },
      { path: '/services/:id/edit', name: 'services-edit', component: { template: '<div />' } },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ServicesListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the services returned by the store with the resolved category name', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services') {
        return Promise.resolve({
          data: {
            data: [RAW_SERVICE_1, RAW_SERVICE_2],
            meta: { page: 1, page_size: 20, total: 2, pages: 1 },
          },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Formatação de Computador')
    expect(wrapper.text()).toContain('Diagnóstico')
    expect(wrapper.text()).toContain('Manutenção')
    expect(wrapper.text()).toContain('2 serviço(s)')
  })

  it('shows an empty state message when there are no services', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhum serviço encontrado.')
  })

  it('navigates to the new-service route when the button is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services') {
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-service-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('services-new')
  })

  it('deletes a service after confirmation and refreshes the list', async () => {
    let servicesCallCount = 0
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services') {
        servicesCallCount += 1
        if (servicesCallCount === 1) {
          return Promise.resolve({
            data: {
              data: [RAW_SERVICE_1],
              meta: { page: 1, page_size: 20, total: 1, pages: 1 },
            },
          }) as never
        }
        return Promise.resolve({
          data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_SERVICE_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/services/service-1')
    expect(servicesCallCount).toBe(2)
  })

  it('navigates to the edit route when the edit icon is clicked', async () => {
    vi.mocked(http.get).mockImplementation((url: string) => {
      if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
      if (url === '/api/v1/services') {
        return Promise.resolve({
          data: { data: [RAW_SERVICE_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
        }) as never
      }
      throw new Error(`unexpected GET ${url}`)
    })
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Editar ${RAW_SERVICE_1.name}"]`).trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('services-edit')
    expect(router.currentRoute.value.params.id).toBe('service-1')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation(
      (url: string, config?: { params?: { page?: number } }) => {
        if (url === '/api/v1/categories') return Promise.resolve(EMPTY_CATEGORY_RESPONSE) as never
        if (url === '/api/v1/services') {
          const page = config?.params?.page ?? 1
          return Promise.resolve({
            data: { data: [RAW_SERVICE_1], meta: { page, page_size: 20, total: 25, pages: 2 } },
          }) as never
        }
        throw new Error(`unexpected GET ${url}`)
      },
    )
    const router = buildRouter()
    router.push('/services')
    await router.isReady()

    const wrapper = mount(ServicesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/services',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/services',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
