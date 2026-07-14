import Aura from '@primevue/themes/aura'
import { definePreset } from '@primevue/themes'

/**
 * Preset customizado sobre o tema Aura do PrimeVue, aplicando a paleta roxa oficial do
 * VeloAI (docs/23-DESIGN-SYSTEM.md).
 */
export const VeloAIPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#F5F3FF',
      100: '#EDE9FE',
      200: '#DDD6FE',
      300: '#C4B5FD',
      400: '#A78BFA',
      500: '#8B5CF6',
      600: '#7C3AED',
      700: '#6D28D9',
      800: '#5B21B6',
      900: '#4C1D95',
      950: '#2E1065',
    },
  },
})
