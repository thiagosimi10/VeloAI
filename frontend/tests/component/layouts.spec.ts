import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/dashboard', name: 'dashboard', component: { template: '<div />' } }],
  })
}

describe('AuthLayout', () => {
  it('renders the VeloAI brand and the slot content', () => {
    const wrapper = mount(AuthLayout, {
      slots: { default: '<p>Conteúdo do formulário</p>' },
    })

    expect(wrapper.text()).toContain('VeloAI')
    expect(wrapper.text()).toContain('Conteúdo do formulário')
  })
})

describe('DefaultLayout', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('renders the header, sidebar and slot content', async () => {
    const router = buildRouter()
    await router.push('/dashboard')

    const wrapper = mount(DefaultLayout, {
      global: { plugins: [router] },
      slots: { default: '<p>Conteúdo da página</p>' },
    })

    expect(wrapper.findComponent({ name: 'AppHeader' }).exists()).toBe(true)
    expect(wrapper.text()).toContain('Conteúdo da página')
  })
})
