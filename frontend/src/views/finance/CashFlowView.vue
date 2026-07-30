<script setup lang="ts">
import { Wallet } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive } from 'vue'

import EmptyState from '@/components/data/EmptyState.vue'
import TableSkeleton from '@/components/data/TableSkeleton.vue'
import MoneyInput from '@/components/form/MoneyInput.vue'
import { type CashFlowEntryType, useCashFlowStore } from '@/stores/cashFlow'

const store = useCashFlowStore()
const toast = useToast()
const typeFilter = computed({
  get: () => store.type,
  set: (value: CashFlowEntryType | null) => {
    store.setTypeFilter(value)
    void store.fetchEntries()
  },
})

const typeLabels: Record<CashFlowEntryType, string> = { in: 'Entrada', out: 'Saída' }

const typeFilterOptions = [
  { label: 'Entrada', value: 'in' },
  { label: 'Saída', value: 'out' },
]

const entryForm = reactive({
  type: 'in' as CashFlowEntryType,
  category: '',
  description: '',
  amount: 0,
})

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

onMounted(() => {
  void store.fetchEntries()
})

async function handleCreateEntry(): Promise<void> {
  const result = await store.createEntry(entryForm)
  if (result) {
    entryForm.category = ''
    entryForm.description = ''
    entryForm.amount = 0
    toast.add({ severity: 'success', summary: 'Lançamento registrado', life: 3000 })
    await store.fetchEntries()
  }
}

const hasPreviousPage = computed(() => store.meta.page > 1)
const hasNextPage = computed(() => store.meta.page < store.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    store.setPage(store.meta.page - 1)
    void store.fetchEntries()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchEntries()
  }
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Fluxo de Caixa</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form
      class="grid grid-cols-1 gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-5"
      @submit.prevent="handleCreateEntry"
    >
      <Select
        v-model="entryForm.type"
        :options="typeFilterOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />
      <InputText v-model="entryForm.category" placeholder="Categoria" class="w-full" />
      <InputText v-model="entryForm.description" placeholder="Descrição" class="w-full" />
      <MoneyInput v-model="entryForm.amount" class="w-full" />
      <Button type="submit" label="Lançar" data-testid="cash-flow-entry-submit" />
    </form>

    <div class="flex flex-wrap gap-2">
      <Select
        v-model="typeFilter"
        :options="typeFilterOptions"
        option-label="label"
        option-value="value"
        show-clear
        placeholder="Filtrar por tipo"
        class="w-full max-w-xs"
      />
    </div>

    <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table class="w-full text-left text-sm">
        <thead class="bg-black/5 dark:bg-white/5">
          <tr>
            <th class="px-4 py-2 font-medium text-text-secondary">Tipo</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Categoria</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Descrição</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Valor</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Data</th>
          </tr>
        </thead>
        <tbody>
          <TableSkeleton v-if="store.isLoading && store.items.length === 0" :columns="5" />
          <tr v-else-if="store.items.length === 0">
            <td colspan="5">
              <EmptyState :icon="Wallet" message="Nenhum lançamento encontrado." />
            </td>
          </tr>
          <tr
            v-for="entry in store.items"
            :key="entry.id"
            class="border-t border-black/5 dark:border-white/10"
          >
            <td class="px-4 py-2">{{ typeLabels[entry.type] }}</td>
            <td class="px-4 py-2">{{ entry.category }}</td>
            <td class="px-4 py-2">{{ entry.description ?? '—' }}</td>
            <td class="px-4 py-2">{{ formatCurrency(entry.amount) }}</td>
            <td class="px-4 py-2">{{ formatDate(entry.date) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between text-sm text-text-secondary">
      <span>{{ store.meta.total }} lançamento(s)</span>
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
