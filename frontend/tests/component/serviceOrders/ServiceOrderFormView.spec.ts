import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ServiceOrderFormView from '@/views/serviceOrders/ServiceOrderFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const EMPTY_CUSTOMERS_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}
const EMPTY_USERS_RESPONSE = {
  data: { data: [], meta: { page: 1, page_size: 100, total: 0, pages: 0 } },
}

const RAW_ORDER = {
  id: 'order-1',
  number: 'OS-2026-000001',
  customer_id: 'customer-1',
  technician_id: null,
  status: 'open' as const,
  equipment: 'Notebook Dell',
  serial_number: null,
  problem: 'Não liga',
  diagnosis: null,
  solution: null,
  total: '0.00',
  opened_at: '2026-01-01T00:00:00Z',
  finished_at: null,
  items: [],
}

function mockLookupFetches(): void {
  vi.mocked(http.get).mockImplementation((url: string) => {
    if (url === '/api/v1/customers') return Promise.resolve(EMPTY_CUSTOMERS_RESPONSE) as never
    if (url === '/api/v1/users') return Promise.resolve(EMPTY_USERS_RESPONSE) as never
    return Promise.reject(new Error(`unexpected GET ${url}`)) as never
  })
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/service-orders', name: 'service-orders', component: { template: '<div />' } },
      {
        path: '/service-orders/new',
        name: 'service-orders-new',
        component: ServiceOrderFormView,
      },
      {
        path: '/service-orders/:id',
        name: 'service-orders-detail',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ServiceOrderFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
  })

  it('renders an empty create form', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/service-orders/new')
    await router.isReady()

    const wrapper = mount(ServiceOrderFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Nova Ordem de Serviço')
    expect((wrapper.find('#service-order-equipment').element as HTMLInputElement).value).toBe('')
  })

  it('creates a service order and redirects to the detail page on success', async () => {
    mockLookupFetches()
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_ORDER } })
    const router = buildRouter()
    router.push('/service-orders/new')
    await router.isReady()

    const wrapper = mount(ServiceOrderFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('#service-order-equipment').setValue('Notebook Dell')
    await wrapper.find('#service-order-problem').setValue('Não liga')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/service-orders',
      expect.objectContaining({ equipment: 'Notebook Dell', problem: 'Não liga' }),
    )
    expect(router.currentRoute.value.name).toBe('service-orders-detail')
    expect(router.currentRoute.value.params.id).toBe('order-1')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    mockLookupFetches()
    const router = buildRouter()
    router.push('/service-orders/new')
    await router.isReady()

    const wrapper = mount(ServiceOrderFormView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('service-orders')
  })
})
