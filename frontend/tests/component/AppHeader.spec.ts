import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import AppHeader from '@/components/layout/AppHeader.vue'

describe('AppHeader', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('renders the AI assistant button and search shortcut', () => {
    const wrapper = mount(AppHeader)

    expect(wrapper.text()).toContain('Perguntar para IA')
    expect(wrapper.text()).toContain('Pesquisar')
  })

  it('toggles the theme when the theme button is clicked', async () => {
    const wrapper = mount(AppHeader)
    await wrapper.vm.$nextTick()

    const themeButton = wrapper.find('[aria-label="Ativar tema escuro"]')
    expect(themeButton.exists()).toBe(true)

    await themeButton.trigger('click')

    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
