<script setup lang="ts">
import { Paperclip, Sparkles, Wrench, X } from 'lucide-vue-next'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import { ref } from 'vue'

import { useAiStore } from '@/stores/ai'

const store = useAiStore()
const prompt = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

async function handleAsk(): Promise<void> {
  const question = prompt.value.trim()
  if (!question) return

  await store.askAI(question)
}

function triggerFilePicker(): void {
  fileInput.value?.click()
}

async function handleFileSelected(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (file) {
    await store.uploadFile(file)
  }
}
</script>

<template>
  <div class="space-y-3 rounded-lg border border-black/10 p-4 dark:border-white/10">
    <h2 class="flex items-center gap-2 text-sm font-semibold text-text-primary dark:text-white">
      <Sparkles :size="16" />
      Assistente de IA
    </h2>

    <div
      v-if="store.attachedFile"
      class="flex items-center gap-2 rounded-md bg-primary/10 px-2.5 py-1.5 text-xs text-primary"
    >
      <Paperclip :size="12" class="shrink-0" />
      <span class="truncate">
        {{ store.attachedFile.filename }} · {{ store.attachedFile.rowCount }} linha(s)
      </span>
      <button
        type="button"
        aria-label="Remover anexo"
        class="ml-auto shrink-0 hover:text-primary-hover"
        @click="store.clearAttachedFile()"
      >
        <X :size="12" />
      </button>
    </div>

    <Textarea
      v-model="prompt"
      data-testid="ai-assistant-prompt"
      class="w-full"
      rows="2"
      placeholder="Pergunte algo sobre o seu negócio, ou anexe uma planilha e peça para importar produtos..."
    />

    <input
      ref="fileInput"
      type="file"
      accept=".csv,.xlsx"
      class="hidden"
      @change="handleFileSelected"
    />

    <div class="flex items-center gap-2">
      <button
        type="button"
        aria-label="Anexar planilha"
        data-testid="ai-assistant-attach-button"
        class="flex items-center gap-1.5 rounded-md border border-black/10 px-3 py-2 text-sm text-text-secondary transition-colors hover:bg-black/5 disabled:opacity-60 dark:border-white/10 dark:hover:bg-white/10"
        :disabled="store.isUploading"
        @click="triggerFilePicker"
      >
        <Paperclip :size="14" />
        {{ store.isUploading ? 'Enviando...' : 'Anexar' }}
      </button>

      <Button
        label="Perguntar"
        data-testid="ai-assistant-ask-button"
        :loading="store.isLoading"
        :disabled="!prompt.trim()"
        @click="handleAsk"
      />
    </div>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <div
      v-if="store.lastResult"
      data-testid="ai-assistant-response"
      class="rounded-lg bg-black/5 p-3 text-sm text-text-primary dark:bg-white/5 dark:text-white"
    >
      <p class="whitespace-pre-line">{{ store.lastResult.response }}</p>
      <p class="mt-2 text-xs text-text-secondary">
        {{ store.lastResult.model }} · {{ store.lastResult.tokens }} tokens
        <span v-if="store.lastResult.cached">· resposta em cache</span>
      </p>
      <p
        v-if="store.lastResult.toolUsed"
        data-testid="ai-assistant-tool-used"
        class="mt-1 flex items-center gap-1 text-xs text-text-secondary"
      >
        <Wrench :size="12" />
        Ferramenta usada: {{ store.lastResult.toolUsed }}
      </p>
    </div>
  </div>
</template>
