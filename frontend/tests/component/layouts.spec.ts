import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AuthLayout from '@/layouts/AuthLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
      { path: '/customers', name: 'customers', component: { template: '<div />' } },
      { path: '/suppliers', name: 'suppliers', component: { template: '<div />' } },
      { path: '/categories', name: 'categories', component: { template: '<div />' } },
      { path: '/products', name: 'products', component: { template: '<div />' } },
      { path: '/services', name: 'services', component: { template: '<div />' } },
      { path: '/service-orders', name: 'service-orders', component: { template: '<div />' } },
      { path: '/sales', name: 'sales', component: { template: '<div />' } },
      { path: '/accounts-receivable', name: 'accounts-receivable', component: { template: '<div />' } },
      { path: '/accounts-payable', name: 'accounts-payable', component: { template: '<div />' } },
      { path: '/cash-flow', name: 'cash-flow', component: { template: '<div />' } },
      { path: '/knowledge', name: 'knowledge', component: { template: '<div />' } },
      { path: '/billing', name: 'billing', component: { template: '<div />' } },
    ],
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
