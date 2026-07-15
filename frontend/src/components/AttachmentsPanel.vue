<script setup lang="ts">
import { Paperclip } from 'lucide-vue-next'
import Button from 'primevue/button'
import { onMounted, ref, watch } from 'vue'

import { type AttachmentResourceType, useAttachmentsStore } from '@/stores/attachments'

const props = defineProps<{
  resourceType: AttachmentResourceType
  resourceId: string
}>()

const store = useAttachmentsStore()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString('pt-BR')
}

async function loadAttachments(): Promise<void> {
  await store.fetchAttachments(props.resourceType, props.resourceId)
}

onMounted(loadAttachments)
watch(() => props.resourceId, loadAttachments)

function triggerFileSelect(): void {
  fileInput.value?.click()
}

async function handleFileSelected(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  isUploading.value = true
  await store.uploadAttachment(props.resourceType, props.resourceId, file)
  isUploading.value = false
  target.value = ''
  await loadAttachments()
}

async function handleRemove(id: string): Promise<void> {
  if (!window.confirm('Remover este anexo?')) {
    return
  }
  const success = await store.deleteAttachment(id)
  if (success) {
    await loadAttachments()
  }
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-semibold text-text-primary dark:text-white">Anexos</h2>
      <Button
        label="Anexar Arquivo"
        severity="secondary"
        :loading="isUploading"
        data-testid="attach-file-button"
        @click="triggerFileSelect"
      />
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        data-testid="attachment-file-input"
        @change="handleFileSelected"
      />
    </div>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <ul v-if="store.items.length > 0" class="space-y-2">
      <li
        v-for="attachment in store.items"
        :key="attachment.id"
        class="flex items-center justify-between rounded-lg border border-black/10 px-3 py-2 text-sm dark:border-white/10"
      >
        <a
          :href="attachment.url"
          target="_blank"
          rel="noopener"
          class="flex items-center gap-2 text-text-primary hover:text-primary dark:text-white"
        >
          <Paperclip :size="16" />
          <span>{{ attachment.originalFilename }}</span>
        </a>
        <div class="flex items-center gap-3 text-xs text-text-secondary">
          <span>{{ formatSize(attachment.sizeBytes) }}</span>
          <span>{{ formatDate(attachment.createdAt) }}</span>
          <button
            type="button"
            aria-label="Remover anexo"
            class="text-text-secondary hover:text-danger"
            @click="handleRemove(attachment.id)"
          >
            Remover
          </button>
        </div>
      </li>
    </ul>
    <p v-else class="text-sm text-text-secondary">
      {{ store.isLoading ? 'Carregando...' : 'Nenhum anexo.' }}
    </p>
  </div>
</template>
