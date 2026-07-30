<script setup lang="ts">
withDefaults(
  defineProps<{ columns: number; rows?: number; cellClass?: string }>(),
  { rows: 3, cellClass: 'px-4 py-2' },
)

// Larguras alternadas só para o esqueleto não parecer uma grade perfeitamente
// alinhada (mais próximo do conteúdo real que vai substituí-lo).
const widths = ['w-32', 'w-24', 'w-20', 'w-28', 'w-16', 'w-24']
</script>

<template>
  <tr v-for="row in rows" :key="row" class="border-t border-black/5 dark:border-white/10">
    <td v-for="column in columns" :key="column" :class="cellClass">
      <div
        class="h-3.5 animate-pulse rounded bg-black/5 dark:bg-white/10"
        :class="widths[(column - 1) % widths.length]"
      />
    </td>
  </tr>
</template>
