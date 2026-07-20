<script setup lang="ts">
import {
  Ban,
  Building2,
  CircleCheck,
  Clock,
  History,
  LogIn,
  Pencil,
  Plus,
  Wallet,
} from 'lucide-vue-next'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const router = useRouter()

const subscriptionStatusLabels: Record<string, string> = {
  TRIAL: 'Período de Teste',
  ACTIVE: 'Ativa',
  PENDING_PAYMENT: 'Pagamento Pendente',
  OVERDUE: 'Em Atraso',
  SUSPENDED: 'Suspensa',
  CANCELED: 'Cancelada',
  EXPIRED: 'Expirada',
}

const subscriptionStatusStyles: Record<string, string> = {
  TRIAL: 'bg-info/10 text-info',
  ACTIVE: 'bg-success/10 text-success',
  PENDING_PAYMENT: 'bg-warning/10 text-warning',
  OVERDUE: 'bg-danger/10 text-danger',
  SUSPENDED: 'bg-danger/10 text-danger',
  CANCELED: 'bg-black/5 text-text-secondary dark:bg-white/10',
  EXPIRED: 'bg-black/5 text-text-secondary dark:bg-white/10',
}

const tenantStatusLabels: Record<string, string> = {
  PROVISIONING: 'Provisionando',
  ACTIVE: 'Ativa',
  SUSPENDED: 'Suspensa',
  FAILED: 'Falhou',
  CANCELED: 'Cancelada',
}

const tenantStatusStyles: Record<string, string> = {
  PROVISIONING: 'bg-info/10 text-info',
  ACTIVE: 'bg-success/10 text-success',
  SUSPENDED: 'bg-warning/10 text-warning',
  FAILED: 'bg-danger/10 text-danger',
  CANCELED: 'bg-black/5 text-text-secondary dark:bg-white/10',
}

const subscriptionStatusDots: Record<string, string> = {
  TRIAL: 'bg-info',
  ACTIVE: 'bg-success',
  PENDING_PAYMENT: 'bg-warning',
  OVERDUE: 'bg-danger',
  SUSPENDED: 'bg-danger',
  CANCELED: 'bg-text-secondary',
  EXPIRED: 'bg-text-secondary',
}

const tenantStatusDots: Record<string, string> = {
  PROVISIONING: 'bg-info',
  ACTIVE: 'bg-success',
  SUSPENDED: 'bg-warning',
  FAILED: 'bg-danger',
  CANCELED: 'bg-text-secondary',
}

const accessibleStatuses = new Set(['ACTIVE', 'SUSPENDED'])

function formatCurrency(value: string): string {
  return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function goToAuditLog(tenantId: string): void {
  router.push({ name: 'admin-tenant-audit-log', params: { id: tenantId } })
}

function goToNewTenant(): void {
  router.push({ name: 'admin-tenants-new' })
}

function goToEditTenant(tenantId: string): void {
  router.push({ name: 'admin-tenants-edit', params: { id: tenantId } })
}

async function handleImpersonate(tenantId: string): Promise<void> {
  const success = await store.impersonateTenant(tenantId)
  if (success) {
    window.location.href = '/dashboard'
  }
}

async function handleCancel(tenantId: string, legalName: string): Promise<void> {
  if (!window.confirm(`Cancelar a empresa "${legalName}"? O banco de dados dela é mantido.`)) {
    return
  }
  const success = await store.cancelTenant(tenantId)
  if (success) {
    await store.fetchTenants()
  }
}

onMounted(async () => {
  await Promise.all([store.fetchSummary(), store.fetchTenants()])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-text-primary dark:text-white">Empresas</h1>
        <p class="mt-0.5 text-sm text-text-secondary">
          Gerencie as empresas provisionadas na plataforma.
        </p>
      </div>
      <button
        type="button"
        data-testid="new-tenant-button"
        class="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-white shadow-sm transition-all duration-150 hover:bg-primary-hover hover:shadow active:scale-[0.98] active:bg-primary-active focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2"
        @click="goToNewTenant"
      >
        <Plus :size="16" />
        Nova Empresa
      </button>
    </div>

    <p v-if="store.error" class="rounded-md bg-danger/10 px-4 py-2 text-sm text-danger">
      {{ store.error }}
    </p>

    <div v-if="store.summary" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div
        class="flex items-start gap-3 rounded-lg border border-black/5 bg-surface-light p-4 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
          <Building2 :size="18" />
        </div>
        <div>
          <p class="text-xs text-text-secondary">Empresas</p>
          <p class="text-xl font-semibold text-text-primary dark:text-white">
            {{ store.summary.totalTenants }}
          </p>
        </div>
      </div>
      <div
        class="flex items-start gap-3 rounded-lg border border-black/5 bg-surface-light p-4 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-info/10 text-info">
          <Clock :size="18" />
        </div>
        <div>
          <p class="text-xs text-text-secondary">Em Trial</p>
          <p class="text-xl font-semibold text-text-primary dark:text-white">
            {{ store.summary.trialCount }}
          </p>
        </div>
      </div>
      <div
        class="flex items-start gap-3 rounded-lg border border-black/5 bg-surface-light p-4 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-success/10 text-success">
          <CircleCheck :size="18" />
        </div>
        <div>
          <p class="text-xs text-text-secondary">Assinaturas Ativas</p>
          <p class="text-xl font-semibold text-text-primary dark:text-white">
            {{ store.summary.activeCount }}
          </p>
        </div>
      </div>
      <div
        class="flex items-start gap-3 rounded-lg border border-black/5 bg-surface-light p-4 shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-surface-dark"
      >
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-warning/10 text-warning">
          <Wallet :size="18" />
        </div>
        <div>
          <p class="text-xs text-text-secondary">MRR Estimado</p>
          <p class="text-xl font-semibold text-text-primary dark:text-white">
            {{ formatCurrency(store.summary.estimatedMrr) }}
          </p>
        </div>
      </div>
    </div>

    <div
      class="overflow-hidden rounded-lg border border-black/5 bg-surface-light shadow-sm dark:border-white/10 dark:bg-surface-dark"
    >
      <table class="w-full text-left text-sm">
        <thead class="border-b border-black/5 dark:border-white/10">
          <tr>
            <th class="px-5 py-3 font-medium text-text-secondary">Empresa</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Documento</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Status</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Plano</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Assinatura</th>
            <th class="px-5 py-3 font-medium text-text-secondary">Ações</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="store.isLoading && store.tenants.length === 0">
            <tr v-for="n in 3" :key="n" class="border-b border-black/5 last:border-0 dark:border-white/5">
              <td class="px-5 py-4">
                <div class="h-3.5 w-32 animate-pulse rounded bg-black/5 dark:bg-white/10" />
              </td>
              <td class="px-5 py-4">
                <div class="h-3.5 w-24 animate-pulse rounded bg-black/5 dark:bg-white/10" />
              </td>
              <td class="px-5 py-4">
                <div class="h-5 w-16 animate-pulse rounded-full bg-black/5 dark:bg-white/10" />
              </td>
              <td class="px-5 py-4">
                <div class="h-3.5 w-20 animate-pulse rounded bg-black/5 dark:bg-white/10" />
              </td>
              <td class="px-5 py-4">
                <div class="h-5 w-20 animate-pulse rounded-full bg-black/5 dark:bg-white/10" />
              </td>
              <td class="px-5 py-4">
                <div class="h-3.5 w-16 animate-pulse rounded bg-black/5 dark:bg-white/10" />
              </td>
            </tr>
          </template>
          <tr v-else-if="store.tenants.length === 0">
            <td colspan="6" class="px-5 py-16 text-center">
              <div class="flex flex-col items-center gap-3 text-text-secondary">
                <div class="flex h-12 w-12 items-center justify-center rounded-full bg-black/5 dark:bg-white/10">
                  <Building2 :size="22" class="opacity-50" />
                </div>
                <p>Nenhuma empresa cadastrada ainda.</p>
                <button
                  type="button"
                  class="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-primary-hover"
                  @click="goToNewTenant"
                >
                  <Plus :size="14" />
                  Nova Empresa
                </button>
              </div>
            </td>
          </tr>
          <tr
            v-for="tenant in store.tenants"
            :key="tenant.tenantId"
            class="border-b border-black/5 transition-colors last:border-0 hover:bg-black/[0.02] dark:border-white/5 dark:hover:bg-white/[0.03]"
          >
            <td class="px-5 py-3">
              <p class="font-medium text-text-primary dark:text-white">{{ tenant.legalName }}</p>
              <p v-if="tenant.tradeName" class="text-xs text-text-secondary">
                {{ tenant.tradeName }}
              </p>
            </td>
            <td class="px-5 py-3 text-text-secondary">{{ tenant.document }}</td>
            <td class="px-5 py-3">
              <span
                class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
                :class="tenantStatusStyles[tenant.status] ?? 'bg-black/5 text-text-secondary'"
              >
                <span
                  class="h-1.5 w-1.5 rounded-full"
                  :class="tenantStatusDots[tenant.status] ?? 'bg-text-secondary'"
                />
                {{ tenantStatusLabels[tenant.status] ?? tenant.status }}
              </span>
            </td>
            <td class="px-5 py-3">{{ tenant.planName ?? '—' }}</td>
            <td class="px-5 py-3">
              <span
                v-if="tenant.subscriptionStatus"
                class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
                :class="
                  subscriptionStatusStyles[tenant.subscriptionStatus] ??
                  'bg-black/5 text-text-secondary'
                "
              >
                <span
                  class="h-1.5 w-1.5 rounded-full"
                  :class="subscriptionStatusDots[tenant.subscriptionStatus] ?? 'bg-text-secondary'"
                />
                {{ subscriptionStatusLabels[tenant.subscriptionStatus] ?? tenant.subscriptionStatus }}
              </span>
              <span v-else class="text-text-secondary">—</span>
            </td>
            <td class="px-5 py-3">
              <div class="flex items-center gap-1">
                <button
                  v-if="accessibleStatuses.has(tenant.status)"
                  type="button"
                  title="Entrar no sistema desta empresa"
                  :data-testid="`impersonate-button-${tenant.tenantId}`"
                  class="flex items-center gap-1 rounded-md px-2 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                  @click="handleImpersonate(tenant.tenantId)"
                >
                  <LogIn :size="14" />
                  Entrar
                </button>
                <button
                  type="button"
                  title="Ver log de auditoria"
                  :aria-label="`Ver logs de ${tenant.legalName}`"
                  class="rounded-md p-1.5 text-text-secondary transition-colors hover:bg-black/5 hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 dark:hover:bg-white/10 dark:hover:text-white"
                  @click="goToAuditLog(tenant.tenantId)"
                >
                  <History :size="16" />
                </button>
                <button
                  type="button"
                  title="Editar"
                  :aria-label="`Editar ${tenant.legalName}`"
                  class="rounded-md p-1.5 text-text-secondary transition-colors hover:bg-black/5 hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 dark:hover:bg-white/10 dark:hover:text-white"
                  @click="goToEditTenant(tenant.tenantId)"
                >
                  <Pencil :size="16" />
                </button>
                <button
                  v-if="tenant.status !== 'CANCELED'"
                  type="button"
                  title="Cancelar"
                  :aria-label="`Cancelar ${tenant.legalName}`"
                  class="rounded-md p-1.5 text-text-secondary transition-colors hover:bg-danger/10 hover:text-danger focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger/40"
                  @click="handleCancel(tenant.tenantId, tenant.legalName)"
                >
                  <Ban :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
