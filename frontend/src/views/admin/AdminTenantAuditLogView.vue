<script setup lang="ts">
import { ArrowLeft, History } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.params.id as string)

const actionLabels: Record<string, string> = {
  TENANT_PROVISIONING_STARTED: 'Provisionamento iniciado',
  TENANT_PROVISIONING_FINISHED: 'Provisionamento concluído',
  TENANT_PROVISIONING_FAILED: 'Provisionamento falhou',
  ADMIN_TENANT_UPDATED: 'Dados cadastrais atualizados',
  ADMIN_TENANT_CANCELED: 'Empresa cancelada',
  ADMIN_TENANT_IMPERSONATED: 'Acesso via impersonação',
  SUBSCRIPTION_CANCELED: 'Assinatura cancelada',
}

function formatAction(action: string): string {
  return actionLabels[action] ?? action
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString('pt-BR')
}

onMounted(async () => {
  await store.fetchAuditLog(tenantId.value)
})
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-5">
    <button
      type="button"
      class="flex items-center gap-1.5 text-sm text-text-secondary hover:text-primary"
      @click="router.push({ name: 'admin-tenants' })"
    >
      <ArrowLeft :size="14" />
      Voltar para Empresas
    </button>

    <div class="flex items-center gap-3">
      <div class="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
        <History :size="20" />
      </div>
      <div>
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">Log de Auditoria</h1>
        <p class="text-sm text-text-secondary">Histórico de eventos desta empresa.</p>
      </div>
    </div>

    <p v-if="store.error" class="rounded-md bg-danger/10 px-4 py-2 text-sm text-danger">
      {{ store.error }}
    </p>

    <div
      class="overflow-hidden rounded-lg border border-black/5 bg-surface-light shadow-sm dark:border-white/10 dark:bg-surface-dark"
    >
      <table class="w-full text-left text-sm">
        <thead class="border-b border-black/5 dark:border-white/10">
          <tr>
            <th class="px-5 py-3 font-medium text-text-secondary">Ação</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Recurso</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Data</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.auditLog.length === 0">
            <td colspan="3" class="px-5 py-12 text-center">
              <div class="flex flex-col items-center gap-2 text-text-secondary">
                <History :size="28" class="opacity-40" />
                <p>Nenhum evento registrado.</p>
              </div>
            </td>
          </tr>
          <tr
            v-for="entry in store.auditLog"
            :key="entry.id"
            class="border-b border-black/5 last:border-0 hover:bg-black/[0.02] dark:border-white/5 dark:hover:bg-white/[0.03]"
          >
            <td class="px-5 py-3 font-medium text-text-primary dark:text-white">
              {{ formatAction(entry.action) }}
            </td>
            <td class="px-5 py-3 text-text-secondary">{{ entry.resource }}</td>
            <td class="px-5 py-3 text-text-secondary">{{ formatDate(entry.createdAt) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
