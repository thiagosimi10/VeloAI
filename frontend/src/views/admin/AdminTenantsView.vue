<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const router = useRouter()

const statusLabels: Record<string, string> = {
  TRIAL: 'Período de Teste',
  ACTIVE: 'Ativa',
  PENDING_PAYMENT: 'Pagamento Pendente',
  OVERDUE: 'Em Atraso',
  SUSPENDED: 'Suspensa',
  CANCELED: 'Cancelada',
  EXPIRED: 'Expirada',
}

function formatCurrency(value: string): string {
  return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function goToAuditLog(tenantId: string): void {
  router.push({ name: 'admin-tenant-audit-log', params: { id: tenantId } })
}

onMounted(async () => {
  await Promise.all([store.fetchSummary(), store.fetchTenants()])
})
</script>

<template>
  <div class="space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Tenants</h1>

    <p v-if="store.error" class="text-sm text-danger">{{ store.error }}</p>

    <div v-if="store.summary" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Empresas</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.totalTenants }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Em Trial</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.trialCount }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Assinaturas Ativas</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.summary.activeCount }}
        </p>
      </div>
      <div class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">MRR Estimado</p>
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ formatCurrency(store.summary.estimatedMrr) }}
        </p>
      </div>
    </div>

    <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table class="w-full text-left text-sm">
        <thead class="bg-black/5 dark:bg-white/5">
          <tr>
            <th class="px-4 py-2 font-medium text-text-secondary">Empresa</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Documento</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Plano</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Assinatura</th>
            <th class="px-4 py-2 font-medium text-text-secondary">Logs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.tenants.length === 0">
            <td colspan="5" class="px-4 py-6 text-center text-text-secondary">
              Nenhum tenant encontrado.
            </td>
          </tr>
          <tr
            v-for="tenant in store.tenants"
            :key="tenant.tenantId"
            class="border-t border-black/5 dark:border-white/5"
          >
            <td class="px-4 py-2">{{ tenant.legalName }}</td>
            <td class="px-4 py-2">{{ tenant.document }}</td>
            <td class="px-4 py-2">{{ tenant.planName ?? '—' }}</td>
            <td class="px-4 py-2">
              {{
                tenant.subscriptionStatus
                  ? (statusLabels[tenant.subscriptionStatus] ?? tenant.subscriptionStatus)
                  : '—'
              }}
            </td>
            <td class="px-4 py-2">
              <button
                type="button"
                class="text-primary hover:underline"
                :data-testid="`audit-log-link-${tenant.tenantId}`"
                @click="goToAuditLog(tenant.tenantId)"
              >
                Ver logs
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
