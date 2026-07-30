<script setup lang="ts">
import {
  CircleAlert,
  CircleCheck,
  Download,
  FileSpreadsheet,
  Loader2,
} from 'lucide-vue-next'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { ref } from 'vue'

import type { ImportResult } from '@/types/import'

const props = defineProps<{
  title: string
  /** Já pluralizado corretamente, ex.: "produto(s)", "fornecedor(es)". */
  resultNoun: string
  templateFilename: string
  /** Conteúdo completo do CSV modelo (cabeçalho + linha de exemplo), pronto pra baixar. */
  templateContent: string
  importFn: (file: File) => Promise<ImportResult | null>
  errorMessage: string | null
}>()

const visible = defineModel<boolean>('visible', { required: true })
const emit = defineEmits<{ imported: [] }>()

type Phase = 'select' | 'uploading' | 'result'

const phase = ref<Phase>('select')
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const result = ref<ImportResult | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const ACCEPTED_EXTENSIONS = ['.csv', '.xlsx']

function reset(): void {
  phase.value = 'select'
  selectedFile.value = null
  isDragging.value = false
  result.value = null
}

function handleHide(): void {
  reset()
}

function triggerFilePicker(): void {
  fileInput.value?.click()
}

function isAcceptedFile(file: File): boolean {
  const name = file.name.toLowerCase()
  return ACCEPTED_EXTENSIONS.some((extension) => name.endsWith(extension))
}

function handleFileSelected(event: Event): void {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (file && isAcceptedFile(file)) {
    selectedFile.value = file
  }
}

function handleDrop(event: DragEvent): void {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && isAcceptedFile(file)) {
    selectedFile.value = file
  }
}

function downloadTemplate(): void {
  const utf8Bom = String.fromCharCode(0xfeff) // garante que o Excel reconheça acentos ao abrir o CSV
  const blob = new Blob([utf8Bom, props.templateContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = props.templateFilename
  link.click()
  URL.revokeObjectURL(url)
}

async function handleImport(): Promise<void> {
  if (!selectedFile.value) return

  phase.value = 'uploading'
  const outcome = await props.importFn(selectedFile.value)
  if (outcome) {
    result.value = outcome
    phase.value = 'result'
    emit('imported')
  } else {
    phase.value = 'select'
  }
}

function handleConclude(): void {
  visible.value = false
  reset()
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :header="title"
    :style="{ width: '32rem' }"
    :draggable="false"
    @hide="handleHide"
  >
    <div v-if="phase === 'select'" class="space-y-4">
      <div
        class="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-8 text-center transition-colors"
        :class="
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-black/15 hover:border-primary/50 dark:border-white/15'
        "
        @click="triggerFilePicker"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <FileSpreadsheet :size="28" class="text-primary" />
        <p v-if="selectedFile" class="text-sm font-medium text-text-primary dark:text-white">
          {{ selectedFile.name }}
        </p>
        <template v-else>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            Arraste sua planilha aqui ou clique para escolher
          </p>
          <p class="text-xs text-text-secondary">Arquivos .csv ou .xlsx, até 5MB</p>
        </template>
        <input
          ref="fileInput"
          type="file"
          accept=".csv,.xlsx"
          class="hidden"
          @change="handleFileSelected"
        />
      </div>

      <button
        type="button"
        class="flex items-center gap-1.5 text-sm text-primary hover:underline"
        @click="downloadTemplate"
      >
        <Download :size="14" />
        Baixar planilha modelo
      </button>

      <p v-if="errorMessage" class="text-sm text-danger">{{ errorMessage }}</p>

      <div class="flex justify-end gap-2 pt-2">
        <Button type="button" label="Cancelar" severity="secondary" @click="handleConclude" />
        <Button
          type="button"
          label="Importar"
          :disabled="!selectedFile"
          @click="handleImport"
        />
      </div>
    </div>

    <div v-else-if="phase === 'uploading'" class="flex flex-col items-center gap-3 py-10">
      <Loader2 :size="28" class="animate-spin text-primary" />
      <p class="text-sm text-text-secondary">Importando... isso pode levar um instante.</p>
    </div>

    <div v-else-if="phase === 'result' && result" class="space-y-4">
      <div class="flex items-center gap-3 rounded-lg bg-success/10 p-4">
        <CircleCheck :size="24" class="shrink-0 text-success" />
        <p class="text-sm text-text-primary dark:text-white">
          <span class="font-semibold">{{ result.created }}</span> de
          <span class="font-semibold">{{ result.totalRows }}</span> {{ resultNoun }}
          importado(s) com sucesso.
        </p>
      </div>

      <div v-if="result.warnings.length > 0" class="space-y-1.5">
        <p class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-warning">
          <CircleAlert :size="12" />
          Avisos ({{ result.warnings.length }})
        </p>
        <ul class="max-h-32 space-y-1 overflow-y-auto rounded-md bg-warning/5 p-2 text-xs text-text-secondary">
          <li v-for="warning in result.warnings" :key="warning.row">
            Linha {{ warning.row }}: {{ warning.message }}
          </li>
        </ul>
      </div>

      <div v-if="result.errors.length > 0" class="space-y-1.5">
        <p class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-danger">
          <CircleAlert :size="12" />
          Não importados ({{ result.errors.length }})
        </p>
        <ul class="max-h-32 space-y-1 overflow-y-auto rounded-md bg-danger/5 p-2 text-xs text-text-secondary">
          <li v-for="error in result.errors" :key="error.row">
            Linha {{ error.row }}: {{ error.message }}
          </li>
        </ul>
      </div>

      <div class="flex justify-end pt-2">
        <Button type="button" label="Concluir" @click="handleConclude" />
      </div>
    </div>
  </Dialog>
</template>
