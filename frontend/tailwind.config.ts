import type { Config } from 'tailwindcss'

/**
 * Design tokens conforme docs/23-DESIGN-SYSTEM.md. Nunca usar cores ou espaçamentos
 * fora desta escala.
 */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6D28D9',
          hover: '#7C3AED',
          active: '#5B21B6',
        },
        surface: {
          light: '#FFFFFF',
          dark: '#1E293B',
        },
        background: {
          light: '#F8FAFC',
          dark: '#0F172A',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
        },
        success: '#22C55E',
        danger: '#EF4444',
        warning: '#F59E0B',
        info: '#3B82F6',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      spacing: {
        '4.5': '18px',
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '14px',
        xl: '20px',
      },
    },
  },
  plugins: [],
} satisfies Config
