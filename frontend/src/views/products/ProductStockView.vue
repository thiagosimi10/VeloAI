<script setup lang="ts">
import { FlexRender, createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type Product, useProductsStore } from '@/stores/products'
import {
  type StockMovement,
  type StockMovementFormPayload,
  useStockMovementsStore,
} from '@/stores/stockMovements'

const productsStore = useProductsStore()
const movementsStore = useStockMovementsStore()
const route = useRoute()
const router = useRouter()

const productId = computed(() => route.params.id as string)
const product = ref<Product | null>(null)
const isSubmitting = ref(false)

const form = reactive<StockMovementFormPayload>({
  movement: 'in',
  quantity: 1,
  reason: '',
})

const movementTypeOptions = [
  { label: 'Entrada', value: 'in' },
  { label: 'Saída', value: 'out' },
  { label: 'Ajuste (contagem de inventário)', value: 'adjustment' },
]

const movementTypeLabels: Record<string, string> = {
  in: 'Entrada',
  out: 'Saída',
  adjustment: 'Ajuste',
}

const columnHelper = createColumnHelper<StockMovement>()

const columns = [
  columnHelper.accessor((row) => movementTypeLabels[row.movement] ?? row.movement, {
    id: 'movement',
    header: 'Tipo',
  }),
  columnHelper.accessor('quantity', { header: 'Quantidade' }),
  columnHelper.accessor('previousStock', { header: 'Estoque Anterior' }),
  columnHelper.accessor('currentStock', { header: 'Estoque Atual' }),
  columnHelper.accessor('reason', { header: 'Motivo' }),
  columnHelper.accessor((row) => new Date(row.createdAt).toLocaleString('pt-BR'), {
    id: 'createdAt',
    header: 'Data',
  }),
]

const table = useVueTable({
  get data() {
    return movementsStore.items
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
})

async function loadData(): Promise<void> {
  product.value = await productsStore.getProduct(productId.value)
  await movementsStore.fetchMovements(productId.value)
}

onMounted(loadData)

const hasPreviousPage = computed(() => movementsStore.meta.page > 1)
const hasNextPage = computed(() => movementsStore.meta.page < movementsStore.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    movementsStore.setPage(movementsStore.meta.page - 1)
    void movementsStore.fetchMovements(productId.value)
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    movementsStore.setPage(movementsStore.meta.page + 1)
    void movementsStore.fetchMovements(productId.value)
  }
}

async function handleSubmit(): Promise<void> {
  isSubmitting.value = true
  const result = await movementsStore.createMovement(productId.value, form)
  isSubmitting.value = false

  if (result) {
    form.quantity = 1
    form.reason = ''
    movementsStore.setPage(1)
    await loadData()
  }
}
</script>

<template>
  <div class="space-y-5">
    <div>
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">
        Estoque {{ product ? `— ${product.name}` : '' }}
      </h1>
      <p v-if="product" class="text-sm text-text-secondary">
        SKU: {{ product.sku }} · Estoque atual:
        <span class="font-medium text-text-primary dark:text-white">{{ product.stock }}</span>
      </p>
    </div>

    <Message v-if="movementsStore.error" severity="error" :closable="false">
      {{ movementsStore.error }}
    </Message>

    <form
      class="grid grid-cols-1 gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-4"
      @submit.prevent="handleSubmit"
    >
      <div class="space-y-1">
        <label
          for="stock-movement-type"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Tipo
        </label>
        <Select
          v-model="form.movement"
          input-id="stock-movement-type"
          :options="movementTypeOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
      <div class="space-y-1">
        <label
          for="stock-movement-quantity"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Quantidade
        </label>
        <InputNumber
          v-model="form.quantity"
          input-id="stock-movement-quantity"
          :min="1"
          class="w-full"
        />
      </div>
      <div class="space-y-1 sm:col-span-2">
        <label
          for="stock-movement-reason"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Motivo
        </label>
        <InputText id="stock-movement-reason" v-model="form.reason" class="w-full" required />
      </div>
      <div class="sm:col-span-4">
        <Button
          type="submit"
          label="Registrar Movimentação"
          :loading="isSubmitting"
          data-testid="stock-movement-submit"
        />
        <Button
          type="button"
          label="Voltar"
          severity="secondary"
          class="ml-2"
          @click="router.push({ name: 'products' })"
        />
      </div>
    </form>

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
          <tr v-if="movementsStore.items.length === 0">
            <td colspan="6" class="px-4 py-6 text-center text-text-secondary">
              {{ movementsStore.isLoading ? 'Carregando...' : 'Nenhuma movimentação encontrada.' }}
            </td>
          </tr>
          <tr
            v-for="row in table.getRowModel().rows"
            :key="row.id"
            class="border-t border-black/5 dark:border-white/10"
          >
            <td v-for="cell in row.getVisibleCells()" :key="cell.id" class="px-4 py-2">
              <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex items-center justify-between text-sm text-text-secondary">
      <span>{{ movementsStore.meta.total }} movimentação(ões)</span>
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="rounded-md px-2 py-1 disabled:opacity-40"
          :disabled="!hasPreviousPage"
          @click="goToPreviousPage"
        >
          Anterior
        </button>
        <span>
          Página {{ movementsStore.meta.page }} de {{ Math.max(movementsStore.meta.pages, 1) }}
        </span>
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
