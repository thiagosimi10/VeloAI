import { createPinia, setActivePinia } from 'pinia'
import PrimeVue from 'primevue/config'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { VeloAIPreset } from '@/plugins/primevue-theme'
import ChangePasswordView from '@/views/ChangePasswordView.vue'

vi.mock('@/services/http', () => ({
  http: { post: vi.fn(), get: vi.fn(), patch: vi.fn() },
}))

import { http } from '@/services/http'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/change-password', name: 'change-password', component: ChangePasswordView },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
    ],
  })
}

function mountView(router: ReturnType<typeof buildRouter>) {
  return mount(ChangePasswordView, {
    global: { plugins: [router, [PrimeVue, { theme: { preset: VeloAIPreset } }]] },
  })
}

async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ChangePasswordView', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.mocked(http.patch).mockReset()
  })

  it('renders the change password form', async () => {
    const router = buildRouter()
    router.push('/change-password')
    await router.isReady()

    const wrapper = mountView(router)

    expect(wrapper.text()).toContain('Defina uma nova senha')
    expect(wrapper.find('#current-password').exists()).toBe(true)
    expect(wrapper.find('#new-password').exists()).toBe(true)
    expect(wrapper.find('#confirm-password').exists()).toBe(true)
  })

  it('shows a mismatch warning and disables submit when passwords differ', async () => {
    const router = buildRouter()
    router.push('/change-password')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#new-password input').setValue('NovaSenha123!')
    await wrapper.find('#confirm-password input').setValue('Diferente123!')

    expect(wrapper.text()).toContain('As senhas não coincidem')
    expect(http.patch).not.toHaveBeenCalled()
  })

  it('redirects to dashboard after successfully changing the password', async () => {
    vi.mocked(http.patch).mockResolvedValueOnce({ data: { data: {} } })
    const router = buildRouter()
    router.push('/change-password')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#current-password input').setValue('Temp0rary!')
    await wrapper.find('#new-password input').setValue('NovaSenhaForte123!')
    await wrapper.find('#confirm-password input').setValue('NovaSenhaForte123!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(http.patch).toHaveBeenCalledWith('/api/v1/auth/password', {
      current_password: 'Temp0rary!',
      new_password: 'NovaSenhaForte123!',
    })
    expect(router.currentRoute.value.name).toBe('dashboard')
  })

  it('shows an error message when the current password is incorrect', async () => {
    vi.mocked(http.patch).mockRejectedValueOnce(new Error('Senha atual incorreta.'))
    const router = buildRouter()
    router.push('/change-password')
    await router.isReady()

    const wrapper = mountView(router)
    await wrapper.find('#current-password input').setValue('senha-errada')
    await wrapper.find('#new-password input').setValue('NovaSenhaForte123!')
    await wrapper.find('#confirm-password input').setValue('NovaSenhaForte123!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Não foi possível conectar')
  })
})
