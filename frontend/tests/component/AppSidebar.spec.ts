import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import AppSidebar from '@/components/layout/AppSidebar.vue'

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/dashboard', name: 'dashboard', component: { template: '<div />' } }],
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
