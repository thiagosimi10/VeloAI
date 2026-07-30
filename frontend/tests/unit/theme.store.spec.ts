import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useThemeStore } from '@/stores/theme'

describe('theme store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to dark theme when nothing is stored', () => {
    const store = useThemeStore()

    store.initialize()

    expect(store.mode).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('reads a previously persisted light theme', () => {
    localStorage.setItem('veloai:theme', 'light')
    const store = useThemeStore()

    store.initialize()

    expect(store.mode).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('reads a previously persisted theme', () => {
    localStorage.setItem('veloai:theme', 'dark')
    const store = useThemeStore()

    store.initialize()

    expect(store.mode).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggle switches between dark and light and persists the choice', () => {
    const store = useThemeStore()
    store.initialize()

    store.toggle()
    expect(store.mode).toBe('light')
    expect(localStorage.getItem('veloai:theme')).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    store.toggle()
    expect(store.mode).toBe('dark')
    expect(localStorage.getItem('veloai:theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('setTheme applies an explicit theme', () => {
    const store = useThemeStore()

    store.setTheme('dark')

    expect(store.mode).toBe('dark')
    expect(localStorage.getItem('veloai:theme')).toBe('dark')
  })
})
