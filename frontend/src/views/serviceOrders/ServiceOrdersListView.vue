<script setup lang="ts">
import { FlexRender, createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import { Eye, Plus } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useCustomersStore } from '@/stores/customers'
import { type ServiceOrder, type ServiceOrderStatus, useServiceOrdersStore } from '@/stores/serviceOrders'

const store = useServiceOrdersStore()
const customersStore = useCustomersStore()
const router = useRouter()
const searchInput = ref('')
const statusFilter = ref<ServiceOrderStatus | null>(null)

const statusLabels: Record<ServiceOrderStatus, string> = {
  open: 'Aberta',
  in_progress: 'Em Atendimento',
  completed: 'Concluída',
  cancelled: 'Cancelada',
}

const statusFilterOptions = [
  { label: 'Aberta', value: 'open' },
  { label: 'Em Atendimento', value: 'in_progress' },
  { label: 'Concluída', value: 'completed' },
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
  return new Date(value).toLocaleDateString('pt-BR')
}

const columnHelper = createColumnHelper<ServiceOrder>()

const columns = [
  columnHelper.accessor('number', { header: 'Número' }),
  columnHelper.accessor((row) => customerNameById.value.get(row.customerId) ?? '—', {
    id: 'customer',
    header: 'Cliente',
  }),
  columnHelper.accessor((row) => statusLabels[row.status], { id: 'status', header: 'Status' }),
  columnHelper.accessor((row) => formatCurrency(row.total), { id: 'total', header: 'Total' }),
  columnHelper.accessor((row) => formatDate(row.openedAt), { id: 'openedAt', header: 'Abertura' }),
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
  void store.fetchOrders()
  void customersStore.fetchCustomers({ pageSize: 100 })
})

function handleSearchSubmit(): void {
  store.setSearch(searchInput.value)
  void store.fetchOrders()
}

function handleStatusFilterChange(): void {
  store.setStatusFilter(statusFilter.value)
  void store.fetchOrders()
}

function goToNewOrder(): void {
  router.push({ name: 'service-orders-new' })
}

function goToOrderDetail(id: string): void {
  router.push({ name: 'service-orders-detail', params: { id } })
}

const hasPreviousPage = computed(() => store.meta.page > 1)
const hasNextPage = computed(() => store.meta.page < store.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    store.setPage(store.meta.page - 1)
    void store.fetchOrders()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchOrders()
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">Ordens de Serviço</h1>
      <button
        type="button"
        data-testid="new-service-order-button"
        class="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-hover"
        @click="goToNewOrder"
      >
        <Plus :size="16" />
        Nova OS
      </button>
    </div>

    <div class="flex flex-wrap gap-2">
      <form class="flex gap-2" @submit.prevent="handleSearchSubmit">
        <InputText
          v-model="searchInput"
          placeholder="Buscar por número ou problema..."
          class="w-full max-w-sm"
        />
        <Button type="submit" label="Buscar" severity="secondary" />
      </form>
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
            <td colspan="6" class="px-4 py-6 text-center text-text-secondary">
              {{ store.isLoading ? 'Carregando...' : 'Nenhuma Ordem de Serviço encontrada.' }}
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
                  :aria-label="`Ver ${row.original.number}`"
                  class="text-text-secondary hover:text-primary"
                  @click="goToOrderDetail(row.original.id)"
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
      <span>{{ store.meta.total }} ordem(ns) de serviço</span>
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
