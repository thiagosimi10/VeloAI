<script setup lang="ts">
import { X } from 'lucide-vue-next'

import { useAiStore } from '@/stores/ai'

import AiAssistantPanel from './AiAssistantPanel.vue'

const store = useAiStore()
</script>

<template>
  <div
    v-if="store.isChatOpen"
    data-testid="ai-chat-modal"
    class="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] rounded-lg bg-surface-light shadow-lg dark:bg-surface-dark relative"
  >
    <button
      type="button"
      aria-label="Fechar assistente de IA"
      data-testid="ai-chat-close-button"
      class="absolute right-2 top-2 rounded-md p-1 text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
      @click="store.closeChat()"
    >
      <X :size="16" />
    </button>

    <AiAssistantPanel />
  </div>
</template>
