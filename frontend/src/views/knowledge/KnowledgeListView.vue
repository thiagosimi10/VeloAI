<script setup lang="ts">
import { BookOpen, Trash2 } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive } from 'vue'

import EmptyState from '@/components/data/EmptyState.vue'
import { useKnowledgeStore } from '@/stores/knowledge'

const store = useKnowledgeStore()
const confirm = useConfirm()
const toast = useToast()

const documentForm = reactive({
  title: '',
  content: '',
})

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString('pt-BR')
}

onMounted(() => {
  void store.fetchDocuments()
})

async function handleCreateDocument(): Promise<void> {
  const result = await store.createDocument({ ...documentForm })
  if (result) {
    documentForm.title = ''
    documentForm.content = ''
    toast.add({ severity: 'success', summary: 'Documento adicionado', life: 3000 })
    await store.fetchDocuments()
  }
}

function handleDelete(id: string, title: string): void {
  confirm.require({
    header: 'Remover documento',
    message: `Remover "${title}" da base de conhecimento? Esta ação não pode ser desfeita.`,
    acceptProps: { label: 'Remover', severity: 'danger' },
    rejectProps: { label: 'Cancelar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const success = await store.deleteDocument(id)
      if (success) {
        toast.add({ severity: 'success', summary: 'Documento removido', life: 3000 })
        await store.fetchDocuments()
      } else {
        toast.add({
          severity: 'error',
          summary: 'Não foi possível remover',
          detail: store.error ?? undefined,
          life: 4000,
        })
      }
    },
  })
}

const hasPreviousPage = computed(() => store.meta.page > 1)
const hasNextPage = computed(() => store.meta.page < store.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    store.setPage(store.meta.page - 1)
    void store.fetchDocuments()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchDocuments()
  }
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Base de Conhecimento</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form
      class="space-y-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      @submit.prevent="handleCreateDocument"
    >
      <InputText v-model="documentForm.title" placeholder="Título" class="w-full" />
      <Textarea
        v-model="documentForm.content"
        placeholder="Conteúdo (ex.: política de garantia, FAQ...)"
        class="w-full"
        rows="4"
      />
      <Button type="submit" label="Adicionar" data-testid="knowledge-document-submit" />
    </form>

    <div v-if="store.isLoading && store.items.length === 0" class="space-y-2">
      <div
        v-for="n in 3"
        :key="n"
        class="h-20 animate-pulse rounded-lg border border-black/10 bg-black/5 dark:border-white/10 dark:bg-white/5"
      />
    </div>
    <EmptyState
      v-else-if="store.items.length === 0"
      :icon="BookOpen"
      message="Nenhum documento cadastrado."
    />
    <ul v-else class="space-y-2">
      <li
        v-for="document in store.items"
        :key="document.id"
        class="rounded-lg border border-black/10 p-3 dark:border-white/10"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="font-medium text-text-primary dark:text-white">{{ document.title }}</p>
            <p class="mt-1 line-clamp-2 text-sm text-text-secondary">{{ document.content }}</p>
            <p class="mt-1 text-xs text-text-secondary">{{ formatDate(document.createdAt) }}</p>
          </div>
          <button
            type="button"
            :aria-label="`Remover ${document.title}`"
            class="text-text-secondary hover:text-danger"
            @click="handleDelete(document.id, document.title)"
          >
            <Trash2 :size="16" />
          </button>
        </div>
      </li>
    </ul>

    <div class="flex items-center justify-between text-sm text-text-secondary">
      <span>{{ store.meta.total }} documento(s)</span>
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="rounded-md px-2 py-1 disabled:opacity-40"
          :disabled="!hasPreviousPage"
          @click="goToPreviousPage"
        >
          Anterior
        </button>
        <span>Página {{ store.meta.page }} de {{ Math.max(store.meta.pages, 1) }}</span>
        <button
          type="button"
          class="rounded-md px-2 py-1 disabled:opacity-40"
          :disabled="!hasNextPage"
          @click="goToNextPage"
        >
          Próxima
        </button>
      </div>
    </div>
  </div>
</template>
