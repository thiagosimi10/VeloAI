<script setup lang="ts">
import { FlexRender, createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import { History, Pencil, Plus, Trash2 } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useCategoriesStore } from '@/stores/categories'
import { type Product, useProductsStore } from '@/stores/products'

const store = useProductsStore()
const categoriesStore = useCategoriesStore()
const router = useRouter()
const searchInput = ref('')
const categoryFilter = ref<string | null>(null)

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
  columnHelper.accessor((row) => formatCurrency(row.salePrice), { id: 'salePrice', header: 'Preço' }),
  columnHelper.accessor((row) => formatCurrency(row.margin), { id: 'margin', header: 'Margem' }),
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

async function handleDelete(id: string, name: string): Promise<void> {
  if (!window.confirm(`Excluir o produto "${name}"?`)) {
    return
  }
  const success = await store.deleteProduct(id)
  if (success) {
    await store.fetchProducts()
  }
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
            <td colspan="7" class="px-4 py-6 text-center text-text-secondary">
              {{ store.isLoading ? 'Carregando...' : 'Nenhum produto encontrado.' }}
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
