<script setup lang="ts">
import {
  FlexRender,
  createColumnHelper,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  useVueTable,
} from '@tanstack/vue-table'
import { History, Package, Pencil, Plus, Trash2, Upload } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import EmptyState from '@/components/data/EmptyState.vue'
import ImportDialog from '@/components/data/ImportDialog.vue'
import SortableHeader from '@/components/data/SortableHeader.vue'
import TableSkeleton from '@/components/data/TableSkeleton.vue'
import { useCategoriesStore } from '@/stores/categories'
import { type Product, useProductsStore } from '@/stores/products'

const store = useProductsStore()
const categoriesStore = useCategoriesStore()
const router = useRouter()
const confirm = useConfirm()
const toast = useToast()
const searchInput = ref('')
const categoryFilter = ref<string | null>(null)
const sorting = ref<SortingState>([])
const isImportDialogOpen = ref(false)

const IMPORT_TEMPLATE =
  'sku,nome,descricao,categoria,fornecedor,preco_custo,preco_venda,estoque,estoque_minimo,unidade,codigo_barras\n' +
  'PROD-001,Produto Exemplo,Descrição do produto,Categoria X,Fornecedor Y,10.00,19.90,50,5,UN,7891234567890\n'

function handleImportFile(file: File) {
  return store.importProducts(file)
}

function handleImported(): void {
  toast.add({ severity: 'success', summary: 'Importação concluída', life: 3000 })
  void store.fetchProducts()
}

const categoryNameById = computed(() => {
  const map = new Map<string, string>()
  for (const category of categoriesStore.items) {
    map.set(category.id, category.name)
  }
  return map
})

const categoryFilterOptions = computed(() =>
  categoriesStore.items.map((category) => ({ label: category.name, value: category.id })),
)

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const columnHelper = createColumnHelper<Product>()

const columns = [
  columnHelper.accessor('sku', { header: 'SKU' }),
  columnHelper.accessor('name', { header: 'Nome' }),
  columnHelper.accessor((row) => (row.categoryId ? categoryNameById.value.get(row.categoryId) : null) ?? '—', {
    id: 'category',
    header: 'Categoria',
  }),
  columnHelper.accessor('stock', { header: 'Estoque' }),
  columnHelper.accessor('salePrice', { header: 'Preço', cell: (info) => formatCurrency(info.getValue()) }),
  columnHelper.accessor('margin', { header: 'Margem', cell: (info) => formatCurrency(info.getValue()) }),
  columnHelper.display({ id: 'actions', header: 'Ações', enableSorting: false }),
]

const table = useVueTable({
  get data() {
    return store.items
  },
  columns,
  state: {
    get sorting() {
      return sorting.value
    },
  },
  onSortingChange: (updater) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

onMounted(() => {
  void store.fetchProducts()
  void categoriesStore.fetchCategories({ pageSize: 100 })
})

function handleSearchSubmit(): void {
  store.setSearch(searchInput.value)
  void store.fetchProducts()
}

function handleCategoryFilterChange(): void {
  store.setCategoryFilter(categoryFilter.value)
  void store.fetchProducts()
}

function goToNewProduct(): void {
  router.push({ name: 'products-new' })
}

function goToEditProduct(id: string): void {
  router.push({ name: 'products-edit', params: { id } })
}

function goToProductStock(id: string): void {
  router.push({ name: 'products-stock', params: { id } })
}

function handleDelete(id: string, name: string): void {
  confirm.require({
    header: 'Excluir produto',
    message: `Excluir o produto "${name}"? Esta ação não pode ser desfeita.`,
    acceptProps: { label: 'Excluir', severity: 'danger' },
    rejectProps: { label: 'Cancelar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const success = await store.deleteProduct(id)
      if (success) {
        toast.add({ severity: 'success', summary: 'Produto excluído', life: 3000 })
        await store.fetchProducts()
      } else {
        toast.add({
          severity: 'error',
          summary: 'Não foi possível excluir',
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
    void store.fetchProducts()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchProducts()
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">Produtos</h1>
      <div class="flex items-center gap-2">
        <button
          type="button"
          data-testid="import-products-button"
          class="flex items-center gap-2 rounded-md border border-black/10 px-3 py-1.5 text-sm font-medium text-text-primary hover:bg-black/5 dark:border-white/10 dark:text-white dark:hover:bg-white/10"
          @click="isImportDialogOpen = true"
        >
          <Upload :size="16" />
          Importar
        </button>
        <button
          type="button"
          data-testid="new-product-button"
          class="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-hover"
          @click="goToNewProduct"
        >
          <Plus :size="16" />
          Novo Produto
        </button>
      </div>
    </div>

    <ImportDialog
      v-model:visible="isImportDialogOpen"
      title="Importar Produtos"
      result-noun="produto(s)"
      template-filename="modelo-importacao-produtos.csv"
      :template-content="IMPORT_TEMPLATE"
      :import-fn="handleImportFile"
      :error-message="store.error"
      @imported="handleImported"
    />

    <div class="flex flex-wrap gap-2">
      <form class="flex gap-2" @submit.prevent="handleSearchSubmit">
        <InputText
          v-model="searchInput"
          placeholder="Buscar por nome, SKU ou código de barras..."
          class="w-full max-w-sm"
        />
        <Button type="submit" label="Buscar" severity="secondary" />
      </form>
      <Select
        v-model="categoryFilter"
        :options="categoryFilterOptions"
        option-label="label"
        option-value="value"
        show-clear
        placeholder="Filtrar por categoria"
        class="w-full max-w-xs"
        @update:model-value="handleCategoryFilterChange"
      />
    </div>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table class="w-full text-left text-sm">
        <thead class="bg-black/5 dark:bg-white/5">
          <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <th
              v-for="header in headerGroup.headers"
              :key="header.id"
              class="px-4 py-2 font-medium text-text-secondary"
            >
              <SortableHeader :header="header" />
            </th>
          </tr>
        </thead>
        <tbody>
          <TableSkeleton v-if="store.isLoading && store.items.length === 0" :columns="7" />
          <tr v-else-if="store.items.length === 0">
            <td colspan="7">
              <EmptyState
                :icon="Package"
                message="Nenhum produto encontrado."
                action-label="Novo Produto"
                @action="goToNewProduct"
              />
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
                  :aria-label="`Estoque de ${row.original.name}`"
                  class="text-text-secondary hover:text-primary"
                  @click="goToProductStock(row.original.id)"
                >
                  <History :size="16" />
                </button>
                <button
                  type="button"
                  :aria-label="`Editar ${row.original.name}`"
                  class="text-text-secondary hover:text-primary"
                  @click="goToEditProduct(row.original.id)"
                >
                  <Pencil :size="16" />
                </button>
                <button
                  type="button"
                  :aria-label="`Excluir ${row.original.name}`"
                  class="text-text-secondary hover:text-danger"
                  @click="handleDelete(row.original.id, row.original.name)"
                >
                  <Trash2 :size="16" />
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
      <span>{{ store.meta.total }} produto(s)</span>
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
