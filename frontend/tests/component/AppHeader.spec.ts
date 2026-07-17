import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn(), get: vi.fn(), patch: vi.fn() },
}))

import AppHeader from '@/components/layout/AppHeader.vue'
import { http } from '@/services/http'
import { useAiStore } from '@/stores/ai'
import { useAuthStore } from '@/stores/auth'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
      { path: '/login', name: 'login', component: { template: '<div />' } },
    ],
  })
}

describe('AppHeader', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    vi.mocked(http.post).mockReset()
  })

  it('renders the AI assistant button and search shortcut', async () => {
    const router = buildRouter()
    await router.push('/dashboard')
    const wrapper = mount(AppHeader, { global: { plugins: [router] } })

    expect(wrapper.text()).toContain('Perguntar para IA')
    expect(wrapper.text()).toContain('Pesquisar')
  })

  it('toggles the AI chat when the "Perguntar para IA" button is clicked', async () => {
    const router = buildRouter()
    await router.push('/dashboard')
    const aiStore = useAiStore()
    const wrapper = mount(AppHeader, { global: { plugins: [router] } })

    expect(aiStore.isChatOpen).toBe(false)

    await wrapper.find('[data-testid="ask-ai-button"]').trigger('click')

    expect(aiStore.isChatOpen).toBe(true)
  })

  it('toggles the theme when the theme button is clicked', async () => {
    const router = buildRouter()
    await router.push('/dashboard')
    const wrapper = mount(AppHeader, { global: { plugins: [router] } })
    await wrapper.vm.$nextTick()

    const themeButton = wrapper.find('[aria-label="Ativar tema escuro"]')
    expect(themeButton.exists()).toBe(true)

    await themeButton.trigger('click')

    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('shows the user menu with name and email when opened', async () => {
    const router = buildRouter()
    await router.push('/dashboard')
    const authStore = useAuthStore()
    authStore.$patch({
      user: {
        id: '1',
        email: 'maria@empresa.test',
        firstName: 'Maria',
        lastName: 'Souza',
        role: 'Administrador',
        permissions: [],
        mustChangePassword: false,
      },
    })
    const wrapper = mount(AppHeader, { global: { plugins: [router] } })

    await wrapper.find('[aria-label="Menu do usuário"]').trigger('click')

    expect(wrapper.text()).toContain('maria@empresa.test')
    expect(wrapper.text()).toContain('Sair')
  })

  it('logs out and redirects to /login when "Sair" is clicked', async () => {
    vi.mocked(http.post).mockResolvedValueOnce({ data: { data: {} } })
    const router = buildRouter()
    await router.push('/dashboard')
    const authStore = useAuthStore()
    authStore.$patch({
      user: {
        id: '1',
        email: 'maria@empresa.test',
        firstName: 'Maria',
        lastName: 'Souza',
        role: 'Administrador',
        permissions: [],
        mustChangePassword: false,
      },
    })
    const wrapper = mount(AppHeader, { global: { plugins: [router] } })

    await wrapper.find('[aria-label="Menu do usuário"]').trigger('click')
    await wrapper.find('[data-testid="logout-button"]').trigger('click')
    await flushPromises()

    expect(authStore.isAuthenticated).toBe(false)
    expect(router.currentRoute.value.name).toBe('login')
  })
})

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}
