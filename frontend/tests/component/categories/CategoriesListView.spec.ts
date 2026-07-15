import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import CategoriesListView from '@/views/categories/CategoriesListView.vue'

vi.mock('@/services/http', () => ({
  http: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

import { http } from '@/services/http'

const RAW_CATEGORY_1 = {
  id: 'category-1',
  name: 'Armazenamento',
  description: 'SSDs e HDs',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const RAW_CATEGORY_2 = { ...RAW_CATEGORY_1, id: 'category-2', name: 'Redes', description: null }

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/categories', name: 'categories', component: CategoriesListView },
      { path: '/categories/new', name: 'categories-new', component: { template: '<div />' } },
      {
        path: '/categories/:id/edit',
        name: 'categories-edit',
        component: { template: '<div />' },
      },
    ],
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('CategoriesListView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(http.get).mockReset()
    vi.mocked(http.delete).mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the categories returned by the store', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: {
        data: [RAW_CATEGORY_1, RAW_CATEGORY_2],
        meta: { page: 1, page_size: 20, total: 2, pages: 1 },
      },
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Armazenamento')
    expect(wrapper.text()).toContain('Redes')
    expect(wrapper.text()).toContain('2 categoria(s)')
  })

  it('shows an empty state message when there are no categories', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Nenhuma categoria encontrada.')
  })

  it('triggers a new search when the search form is submitted', async () => {
    vi.mocked(http.get).mockResolvedValue({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('input').setValue('armazenamento')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/categories',
      expect.objectContaining({ params: expect.objectContaining({ search: 'armazenamento' }) }),
    )
  })

  it('navigates to the new-category route when the button is clicked', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find('[data-testid="new-category-button"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('categories-new')
  })

  it('deletes a category after confirmation and refreshes the list', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CATEGORY_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    vi.mocked(http.delete).mockResolvedValueOnce({ data: { data: {} } })
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [], meta: { page: 1, page_size: 20, total: 0, pages: 0 } },
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Excluir ${RAW_CATEGORY_1.name}"]`).trigger('click')
    await flushPromises()

    expect(http.delete).toHaveBeenCalledWith('/api/v1/categories/category-1')
    expect(http.get).toHaveBeenCalledTimes(2)
  })

  it('navigates to the edit route when the edit icon is clicked', async () => {
    vi.mocked(http.get).mockResolvedValueOnce({
      data: { data: [RAW_CATEGORY_1], meta: { page: 1, page_size: 20, total: 1, pages: 1 } },
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    await wrapper.find(`[aria-label="Editar ${RAW_CATEGORY_1.name}"]`).trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('categories-edit')
    expect(router.currentRoute.value.params.id).toBe('category-1')
  })

  it('paginates to the next and back to the previous page', async () => {
    vi.mocked(http.get).mockImplementation((_url: string, config?: { params?: { page?: number } }) => {
      const page = config?.params?.page ?? 1
      return Promise.resolve({
        data: { data: [RAW_CATEGORY_1], meta: { page, page_size: 20, total: 25, pages: 2 } },
      }) as never
    })
    const router = buildRouter()
    router.push('/categories')
    await router.isReady()

    const wrapper = mount(CategoriesListView, {
      global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
    })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((btn) => btn.text() === 'Próxima')
    await nextButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/categories',
      expect.objectContaining({ params: expect.objectContaining({ page: 2 }) }),
    )

    const previousButton = wrapper.findAll('button').find((btn) => btn.text() === 'Anterior')
    await previousButton?.trigger('click')
    await flushPromises()

    expect(http.get).toHaveBeenLastCalledWith(
      '/api/v1/categories',
      expect.objectContaining({ params: expect.objectContaining({ page: 1 }) }),
    )
  })
})
