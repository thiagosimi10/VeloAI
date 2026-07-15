<script setup lang="ts">
import { FlexRender, createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import { Eye, Plus } from 'lucide-vue-next'
import Select from 'primevue/select'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type AccountReceivable, type AccountReceivableStatus, useAccountsReceivableStore } from '@/stores/accountsReceivable'
import { useCustomersStore } from '@/stores/customers'

const store = useAccountsReceivableStore()
const customersStore = useCustomersStore()
const router = useRouter()
const statusFilter = ref<AccountReceivableStatus | null>(null)

const statusLabels: Record<AccountReceivableStatus, string> = {
  pending: 'Pendente',
  received: 'Recebida',
  cancelled: 'Cancelada',
}

const statusFilterOptions = [
  { label: 'Pendente', value: 'pending' },
  { label: 'Recebida', value: 'received' },
  { label: 'Cancelada', value: 'cancelled' },
]

const customerNameById = computed(() => {
  const map = new Map<string, string>()
  for (const customer of customersStore.items) {
    map.set(customer.id, customer.name)
  }
  return map
})

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

function statusLabel(receivable: AccountReceivable): string {
  const label = statusLabels[receivable.status]
  return receivable.isOverdue ? `${label} (Vencida)` : label
}

const columnHelper = createColumnHelper<AccountReceivable>()

const columns = [
  columnHelper.accessor((row) => customerNameById.value.get(row.customerId) ?? '—', {
    id: 'customer',
    header: 'Cliente',
  }),
  columnHelper.accessor((row) => formatDate(row.dueDate), { id: 'dueDate', header: 'Vencimento' }),
  columnHelper.accessor((row) => formatCurrency(row.amount), { id: 'amount', header: 'Valor' }),
  columnHelper.accessor((row) => statusLabel(row), { id: 'status', header: 'Status' }),
  columnHelper.display({ id: 'actions', header: 'Ações' }),
]

const table = useVueTable({
  get data() {
    return store.items
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
})

onMounted(() => {
  void store.fetchReceivables()
  void customersStore.fetchCustomers({ pageSize: 100 })
})

function handleStatusFilterChange(): void {
  store.setStatusFilter(statusFilter.value)
  void store.fetchReceivables()
}

function goToNewReceivable(): void {
  router.push({ name: 'accounts-receivable-new' })
}

function goToReceivableDetail(id: string): void {
  router.push({ name: 'accounts-receivable-detail', params: { id } })
}

const hasPreviousPage = computed(() => store.meta.page > 1)
const hasNextPage = computed(() => store.meta.page < store.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    store.setPage(store.meta.page - 1)
    void store.fetchReceivables()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchReceivables()
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">Contas a Receber</h1>
      <button
        type="button"
        data-testid="new-receivable-button"
        class="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-hover"
        @click="goToNewReceivable"
      >
        <Plus :size="16" />
        Nova Conta a Receber
      </button>
    </div>

    <div class="flex flex-wrap gap-2">
      <Select
        v-model="statusFilter"
        :options="statusFilterOptions"
        option-label="label"
        option-value="value"
        show-clear
        placeholder="Filtrar por status"
        class="w-full max-w-xs"
        @update:model-value="handleStatusFilterChange"
      />
    </div>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table class="w-full text-left text-sm">
        <thead class="bg-black/5 dark:bg-white/5">
          <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <th
              v-for="header in headerGroup.headers"
              :key="header.id"
              class="px-4 py-2 font-medium text-text-secondary"
            >
              <FlexRender
                v-if="!header.isPlaceholder"
                :render="header.column.columnDef.header"
                :props="header.getContext()"
              />
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.items.length === 0">
            <td colspan="5" class="px-4 py-6 text-center text-text-secondary">
              {{ store.isLoading ? 'Carregando...' : 'Nenhuma Conta a Receber encontrada.' }}
            </td>
          </tr>
          <tr
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="border-t border-black/5 dark:border-white/10"
          >
            <td v-for="cell in row.getVisibleCells()" :key="cell.id" class="px-4 py-2">
              <div v-if="cell.column.id === 'actions'" class="flex gap-3">
                <button
                  type="button"
                  aria-label="Ver conta a receber"
                  class="text-text-secondary hover:text-primary"
                  @click="goToReceivableDetail(row.original.id)"
                >
                  <Eye :size="16" />
                </button>
              </div>
              <FlexRender
                v-else
                :render="cell.column.columnDef.cell"
                :props="cell.getContext()"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between text-sm text-text-secondary">
      <span>{{ store.meta.total }} conta(s) a receber</span>
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
