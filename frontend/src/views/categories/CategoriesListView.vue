<script setup lang="ts">
import { FlexRender, createColumnHelper, getCoreRowModel, useVueTable } from '@tanstack/vue-table'
import { Pencil, Plus, Trash2 } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type Category, useCategoriesStore } from '@/stores/categories'

const store = useCategoriesStore()
const router = useRouter()
const searchInput = ref('')

const columnHelper = createColumnHelper<Category>()

const columns = [
  columnHelper.accessor('name', { header: 'Nome' }),
  columnHelper.accessor((row) => row.description ?? '—', {
    id: 'description',
    header: 'Descrição',
  }),
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
  void store.fetchCategories()
})

function handleSearchSubmit(): void {
  store.setSearch(searchInput.value)
  void store.fetchCategories()
}

function goToNewCategory(): void {
  router.push({ name: 'categories-new' })
}

function goToEditCategory(id: string): void {
  router.push({ name: 'categories-edit', params: { id } })
}

async function handleDelete(id: string, name: string): Promise<void> {
  if (!window.confirm(`Excluir a categoria "${name}"?`)) {
    return
  }
  const success = await store.deleteCategory(id)
  if (success) {
    await store.fetchCategories()
  }
}

const hasPreviousPage = computed(() => store.meta.page > 1)
const hasNextPage = computed(() => store.meta.page < store.meta.pages)

function goToPreviousPage(): void {
  if (hasPreviousPage.value) {
    store.setPage(store.meta.page - 1)
    void store.fetchCategories()
  }
}

function goToNextPage(): void {
  if (hasNextPage.value) {
    store.setPage(store.meta.page + 1)
    void store.fetchCategories()
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">Categorias</h1>
      <button
        type="button"
        data-testid="new-category-button"
        class="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-hover"
        @click="goToNewCategory"
      >
        <Plus :size="16" />
        Nova Categoria
      </button>
    </div>

    <form class="flex gap-2" @submit.prevent="handleSearchSubmit">
      <InputText v-model="searchInput" placeholder="Buscar por nome..." class="w-full max-w-sm" />
      <Button type="submit" label="Buscar" severity="secondary" />
    </form>

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
            <td colspan="3" class="px-4 py-6 text-center text-text-secondary">
              {{ store.isLoading ? 'Carregando...' : 'Nenhuma categoria encontrada.' }}
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
                  :aria-label="`Editar ${row.original.name}`"
                  class="text-text-secondary hover:text-primary"
                  @click="goToEditCategory(row.original.id)"
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
      <span>{{ store.meta.total }} categoria(s)</span>
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
