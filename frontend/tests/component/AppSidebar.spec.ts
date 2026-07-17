import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AppSidebar from '@/components/layout/AppSidebar.vue'

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

describe('AppSidebar', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('renders the VeloAI logo and the Dashboard link when expanded', async () => {
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(AppSidebar, { global: { plugins: [router] } })

    expect(wrapper.text()).toContain('VeloAI')
    expect(wrapper.text()).toContain('Dashboard')
  })

  it('collapses and hides labels when the toggle button is clicked', async () => {
    const router = buildRouter()
    router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(AppSidebar, { global: { plugins: [router] } })

    await wrapper.find('button').trigger('click')

    expect(wrapper.text()).not.toContain('VeloAI')
    expect(localStorage.getItem('veloai:sidebar-collapsed')).toBe('true')
  })
})
