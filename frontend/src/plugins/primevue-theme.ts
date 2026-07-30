import Aura from '@primevue/themes/aura'
import { definePreset } from '@primevue/themes'

/**
 * Preset customizado sobre o tema Aura do PrimeVue, aplicando a paleta roxa oficial do
 * VeloAI (docs/23-DESIGN-SYSTEM.md).
 */
// O Aura resolve `colorScheme.{light,dark}.primary.color` para `{primary.500}`/
// `{primary.400}` por padrão — sem este bloco, todo componente PrimeVue (Button,
// InputNumber, links de foco, etc.) renderiza um roxo mais claro (#8B5CF6/#A78BFA) que
// nunca bate com o `bg-primary` (#6D28D9) usado nos componentes em Tailwind puro,
// resultando em duas cores de marca diferentes na mesma tela.
const PRIMARY_COLOR_SCHEME = {
  color: '{primary.700}', // #6D28D9 — mesmo valor de `primary.DEFAULT` no tailwind.config.ts
  contrastColor: '#ffffff',
  hoverColor: '{primary.600}', // #7C3AED — mesmo valor de `primary.hover`
  activeColor: '{primary.800}', // #5B21B6 — mesmo valor de `primary.active`
}

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
    colorScheme: {
      light: {
        primary: PRIMARY_COLOR_SCHEME,
        formField: {
          invalidBorderColor: '#EF4444', // mesmo valor de `danger` no tailwind.config.ts
        },
      },
      dark: {
        primary: PRIMARY_COLOR_SCHEME,
        // O Aura usa `{zinc.*}` para as superfícies no modo escuro por padrão — a
        // paleta do VeloAI é toda baseada em `{slate.*}` (`background.dark` #0F172A =
        // slate-900, `surface.dark` #1E293B = slate-800), então sem isto os
        // componentes PrimeVue (Dialog, Select, DataTable...) renderiam num cinza
        // ligeiramente diferente do resto da interface no modo escuro.
        surface: {
          0: '#ffffff',
          50: '{slate.50}',
          100: '{slate.100}',
          200: '{slate.200}',
          300: '{slate.300}',
          400: '{slate.400}',
          500: '{slate.500}',
          600: '{slate.600}',
          700: '{slate.700}',
          800: '{slate.800}',
          900: '{slate.900}',
          950: '{slate.950}',
        },
        formField: {
          invalidBorderColor: '#EF4444',
        },
      },
    },
  },
})
