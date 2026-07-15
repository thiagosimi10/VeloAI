import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import NotFoundView from '@/views/NotFoundView.vue'

describe('NotFoundView', () => {
  it('renders a 404 message with a link back to the dashboard', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/dashboard', name: 'dashboard', component: { template: '<div />' } }],
    })
    await router.push('/dashboard')

    const wrapper = mount(NotFoundView, { global: { plugins: [router] } })

    expect(wrapper.text()).toContain('404')
    expect(wrapper.findComponent({ name: 'RouterLink' }).exists()).toBe(true)
  })
})
