<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import { ref } from 'vue'

import { useAiStore } from '@/stores/ai'

const store = useAiStore()
const prompt = ref('')

async function handleAsk(): Promise<void> {
  const question = prompt.value.trim()
  if (!question) return

  await store.askAI(question)
}
</script>

<template>
  <div class="space-y-3 rounded-lg border border-black/10 p-4 dark:border-white/10">
    <h2 class="flex items-center gap-2 text-sm font-semibold text-text-primary dark:text-white">
      <Sparkles :size="16" />
      Assistente de IA
    </h2>

    <Textarea
      v-model="prompt"
      data-testid="ai-assistant-prompt"
      class="w-full"
      rows="2"
      placeholder="Pergunte algo sobre o seu negócio..."
    />

    <Button
      label="Perguntar"
      data-testid="ai-assistant-ask-button"
      :loading="store.isLoading"
      :disabled="!prompt.trim()"
      @click="handleAsk"
    />

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
    </div>
  </div>
</template>
