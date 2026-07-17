<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.params.id as string)

function formatDate(value: string): string {
  return new Date(value).toLocaleString('pt-BR')
}

onMounted(async () => {
  await store.fetchAuditLog(tenantId.value)
})
</script>

<template>
  <div class="space-y-5">
    <button
      type="button"
      class="text-sm text-text-secondary hover:text-primary"
      @click="router.push({ name: 'admin-tenants' })"
    >
      ← Voltar para Tenants
    </button>

    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Log de Auditoria</h1>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table class="w-full text-left text-sm">
        <thead class="bg-black/5 dark:bg-white/5">
          <tr>
            <th class="px-4 py-2 font-medium text-text-secondary">Ação</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Recurso</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Data</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.auditLog.length === 0">
            <td colspan="3" class="px-4 py-6 text-center text-text-secondary">
              Nenhum evento registrado.
            </td>
          </tr>
          <tr
            v-for="entry in store.auditLog"
            :key="entry.id"
            class="border-t border-black/5 dark:border-white/5"
          >
            <td class="px-4 py-2">{{ entry.action }}</td>
            <td class="px-4 py-2">{{ entry.resource }}</td>
            <td class="px-4 py-2">{{ formatDate(entry.createdAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
