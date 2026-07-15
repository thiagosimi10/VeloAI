import { AxiosError, AxiosHeaders } from 'axios'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import CategoryFormView from '@/views/categories/CategoryFormView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CATEGORY = {
  id: 'category-1',
  name: 'Armazenamento',
  description: 'SSDs e HDs',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/categories', name: 'categories', component: { template: '<div />' } },
      { path: '/categories/new', name: 'categories-new', component: CategoryFormView },
      { path: '/categories/:id/edit', name: 'categories-edit', component: CategoryFormView },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(CategoryFormView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('CategoryFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.post).mockReset()
    vi.mocked(http.patch).mockReset()
  })

  it('renders an empty create form', async () => {
    const router = buildRouter()
    router.push('/categories/new')
    await router.isReady()

    const wrapper = mountView(router)

    expect(wrapper.text()).toContain('Nova Categoria')
    expect((wrapper.find('#category-name').element as HTMLInputElement).value).toBe('')
  })

  it('creates a category and redirects to the list on success', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: RAW_CATEGORY } })
    const router = buildRouter()
    router.push('/categories/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#category-name').setValue('Armazenamento')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.post).toHaveBeenCalledWith(
      '/api/v1/categories',
      expect.objectContaining({ name: 'Armazenamento' }),
    )
    expect(router.currentRoute.value.name).toBe('categories')
  })

  it('shows an error message and stays on the page when creation fails', async () => {
    const error = new AxiosError('Conflict', '409', undefined, undefined, {
      status: 409,
      statusText: 'Conflict',
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
      data: { message: 'Categoria já cadastrada.' },
    } as never)
    vi.mocked(http.post).mockRejectedValueOnce(error)
    const router = buildRouter()
    router.push('/categories/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#category-name').setValue('Armazenamento')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Categoria já cadastrada.')
    expect(router.currentRoute.value.name).toBe('categories-new')
  })

  it('loads existing category data in edit mode', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_CATEGORY } })
    const router = buildRouter()
    router.push('/categories/category-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Editar Categoria')
    expect((wrapper.find('#category-name').element as HTMLInputElement).value).toBe(
      'Armazenamento',
    )
  })

  it('updates a category and redirects to the list on success', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({ data: { data: RAW_CATEGORY } })
    vi.mocked(http.patch).mockResolvedValueOnce({
      data: { data: { ...RAW_CATEGORY, name: 'Armazenamento e Backup' } },
    })
    const router = buildRouter()
    router.push('/categories/category-1/edit')
    await router.isReady()

    const wrapper = mountView(router)
    await flushPromises()
    await wrapper.vm.$nextTick()

    await wrapper.find('#category-name').setValue('Armazenamento e Backup')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith(
      '/api/v1/categories/category-1',
      expect.objectContaining({ name: 'Armazenamento e Backup' }),
    )
    expect(router.currentRoute.value.name).toBe('categories')
  })

  it('navigates back to the list when cancel is clicked', async () => {
    const router = buildRouter()
    router.push('/categories/new')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('button[type="button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('categories')
  })
})
