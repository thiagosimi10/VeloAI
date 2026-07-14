import { defineStore } from 'pinia'

export type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'veloai:theme'

function applyThemeClass(mode: ThemeMode): void {
  document.documentElement.classList.toggle('dark', mode === 'dark')
}

function readStoredTheme(): ThemeMode {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') {
    return stored
  }
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
  return prefersDark ? 'dark' : 'light'
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: 'light' as ThemeMode,
  }),
  actions: {
    initialize(): void {
      this.mode = readStoredTheme()
      applyThemeClass(this.mode)
    },
    setTheme(mode: ThemeMode): void {
      this.mode = mode
      localStorage.setItem(STORAGE_KEY, mode)
      applyThemeClass(mode)
    },
    toggle(): void {
      this.setTheme(this.mode === 'dark' ? 'light' : 'dark')
    },
  },
})
