<script setup lang="ts" generic="TData">
import { FlexRender, type Header } from '@tanstack/vue-table'
import { ChevronDown, ChevronUp, ChevronsUpDown } from 'lucide-vue-next'

defineProps<{ header: Header<TData, unknown> }>()
</script>

<template>
  <button
    v-if="header.column.getCanSort()"
    type="button"
    class="flex items-center gap-1 hover:text-text-primary dark:hover:text-white"
    @click="header.column.getToggleSortingHandler()?.($event)"
  >
    <FlexRender :render="header.column.columnDef.header" :props="header.getContext()" />
    <ChevronUp v-if="header.column.getIsSorted() === 'asc'" :size="14" />
    <ChevronDown v-else-if="header.column.getIsSorted() === 'desc'" :size="14" />
    <ChevronsUpDown v-else :size="14" class="opacity-40" />
  </button>
  <FlexRender
    v-else-if="!header.isPlaceholder"
    :render="header.column.columnDef.header"
    :props="header.getContext()"
  />
</template>
