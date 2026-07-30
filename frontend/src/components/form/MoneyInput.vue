<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: number | null
    disabled?: boolean
  }>(),
  { disabled: false },
)

const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

/**
 * Guarda o valor em centavos (inteiro) — nunca em ponto flutuante. Cada dígito
 * digitado sempre entra pela direita, tipo calculadora/maquininha de cartão, então
 * nunca importa onde o cursor visualmente está: dá pra clicar em qualquer lugar do
 * campo e sair digitando, sem precisar reposicionar nada (esse era o problema do
 * InputNumber do PrimeVue, cujo cursor "pula" ao formatar o milhar).
 */
const MAX_CENTS = 99_999_999_999

function toCents(value: number | null): number {
  if (value === null || Number.isNaN(value)) return 0
  return Math.round(value * 100)
}

const cents = ref(toCents(props.modelValue))

watch(
  () => props.modelValue,
  (value) => {
    const next = toCents(value)
    if (next !== cents.value) {
      cents.value = next
    }
  },
)

const displayValue = computed(() =>
  (cents.value / 100).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
)

function emitValue(): void {
  emit('update:modelValue', Number((cents.value / 100).toFixed(2)))
}

function handleKeydown(event: KeyboardEvent): void {
  if (props.disabled) return

  if (/^[0-9]$/.test(event.key)) {
    event.preventDefault()
    if (cents.value < MAX_CENTS) {
      cents.value = cents.value * 10 + Number(event.key)
      emitValue()
    }
    return
  }

  if (event.key === 'Backspace' || event.key === 'Delete') {
    event.preventDefault()
    cents.value = Math.floor(cents.value / 10)
    emitValue()
    return
  }

  const allowedKeys = [
    'Tab',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Home',
    'End',
    'Enter',
    'Escape',
  ]
  if (allowedKeys.includes(event.key) || event.ctrlKey || event.metaKey) {
    return
  }

  event.preventDefault()
}

function handlePaste(event: ClipboardEvent): void {
  event.preventDefault()
  if (props.disabled) return

  const digitsOnly = (event.clipboardData?.getData('text') ?? '').replace(/\D/g, '')
  if (!digitsOnly) return

  cents.value = Math.min(Number(digitsOnly), MAX_CENTS)
  emitValue()
}

function moveCursorToEnd(event: FocusEvent | MouseEvent): void {
  const input = event.target as HTMLInputElement
  requestAnimationFrame(() => {
    input.setSelectionRange(input.value.length, input.value.length)
  })
}
</script>

<template>
  <input
    type="text"
    inputmode="numeric"
    :value="displayValue"
    :disabled="disabled"
    class="rounded-md border border-black/10 bg-transparent px-3 py-2 text-right text-sm text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-60 dark:border-white/10 dark:text-white"
    @keydown="handleKeydown"
    @paste="handlePaste"
    @focus="moveCursorToEnd"
    @click="moveCursorToEnd"
  />
</template>
