<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon: Component
  message: string
  actionLabel?: string
}>()

const emit = defineEmits<{ action: [] }>()
</script>

<template>
  <div class="flex flex-col items-center gap-3 py-10 text-text-secondary">
    <div class="flex h-12 w-12 items-center justify-center rounded-full bg-black/5 dark:bg-white/10">
      <component :is="icon" :size="22" class="opacity-50" />
    </div>
    <p>{{ message }}</p>
    <button
      v-if="actionLabel"
      type="button"
      class="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-primary-hover"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>
