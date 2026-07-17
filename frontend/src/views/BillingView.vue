<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { computed, onMounted } from 'vue'

import { useBillingStore } from '@/stores/billing'

const store = useBillingStore()

const statusLabels: Record<string, string> = {
  TRIAL: 'Período de Teste',
  ACTIVE: 'Ativa',
  PENDING_PAYMENT: 'Pagamento Pendente',
  OVERDUE: 'Em Atraso',
  SUSPENDED: 'Suspensa',
  CANCELED: 'Cancelada',
  EXPIRED: 'Expirada',
}

const statusLabel = computed(
  () => statusLabels[store.subscription?.status ?? ''] ?? store.subscription?.status,
)

const canCancel = computed(() => {
  const status = store.subscription?.status
  return status !== undefined && status !== 'CANCELED'
})

function formatCurrency(value: string): string {
  return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString('pt-BR')
}

async function handleCancel(): Promise<void> {
  if (!window.confirm('Cancelar sua assinatura?')) {
    return
  }
  await store.cancelSubscription()
}

onMounted(async () => {
  await store.fetchSubscription()
})
</script>

<template>
  <div class="space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Assinatura</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <template v-if="store.subscription">
      <div class="flex items-center justify-between">
        <p class="text-lg font-semibold text-text-primary dark:text-white">
          {{ store.subscription.planName }}
        </p>
        <span
          data-testid="subscription-status"
          class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary"
        >
          {{ statusLabel }}
        </span>
      </div>

      <div class="grid grid-cols-2 gap-4 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-3">
        <div>
          <p class="text-xs text-text-secondary">Valor</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(store.subscription.planPrice) }} / mês
          </p>
        </div>
        <div v-if="store.subscription.status === 'TRIAL'">
          <p class="text-xs text-text-secondary">Dias Restantes do Trial</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ store.subscription.daysRemaining }}
          </p>
        </div>
        <div v-if="store.subscription.trialEndsAt">
          <p class="text-xs text-text-secondary">Fim do Trial</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatDate(store.subscription.trialEndsAt) }}
          </p>
        </div>
      </div>

      <div
        v-if="canCancel"
        class="flex flex-wrap gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <Button
          label="Cancelar Assinatura"
          severity="secondary"
          data-testid="cancel-subscription-button"
          @click="handleCancel"
        />
      </div>
    </template>
    <p v-else-if="store.isLoading" class="text-sm text-text-secondary">Carregando...</p>
  </div>
</template>
