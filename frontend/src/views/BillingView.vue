<script setup lang="ts">
import { Check, CircleAlert, Clock, Lock, ShieldCheck } from 'lucide-vue-next'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { type PlanTier, useBillingStore } from '@/stores/billing'

const store = useBillingStore()
const route = useRoute()
const confirm = useConfirm()
const toast = useToast()

const checkoutBanners: Record<string, { severity: 'success' | 'warn'; text: string }> = {
  success: {
    severity: 'success',
    text: 'Pagamento recebido! Pode levar alguns instantes para confirmarmos — atualize a página se o status ainda não mudou.',
  },
  cancel: { severity: 'warn', text: 'Checkout cancelado. Nenhuma cobrança foi feita.' },
  expired: { severity: 'warn', text: 'O checkout expirou antes do pagamento. Tente novamente.' },
}

const checkoutBanner = computed(() => {
  const status = route.query.checkout
  return typeof status === 'string' ? (checkoutBanners[status] ?? null) : null
})

const baseMonthlyPrice = computed(() => {
  const monthly = store.planTiers.find((tier) => tier.cycle === 'MONTHLY')
  return monthly ? Number(monthly.monthlyPrice) : null
})

function savingsPercent(tier: PlanTier): number | null {
  if (baseMonthlyPrice.value === null || baseMonthlyPrice.value === 0) {
    return null
  }
  const percent = (1 - Number(tier.monthlyPrice) / baseMonthlyPrice.value) * 100
  return percent > 0 ? Math.round(percent) : null
}

async function handleSubscribe(cycle: string): Promise<void> {
  const checkoutUrl = await store.createCheckout(cycle)
  if (checkoutUrl) {
    window.location.href = checkoutUrl
  }
}

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

function handleCancel(): void {
  confirm.require({
    header: 'Cancelar assinatura',
    message: 'Cancelar sua assinatura? Você perde acesso ao sistema quando o período atual terminar.',
    acceptProps: { label: 'Cancelar Assinatura', severity: 'danger' },
    rejectProps: { label: 'Voltar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const success = await store.cancelSubscription()
      if (success) {
        toast.add({ severity: 'success', summary: 'Assinatura cancelada', life: 3000 })
      }
    },
  })
}

onMounted(async () => {
  await Promise.all([store.fetchSubscription(), store.fetchPlanTiers()])
})
</script>

<template>
  <div class="space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Assinatura</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>
    <Message v-if="checkoutBanner" :severity="checkoutBanner.severity" :closable="false">
      {{ checkoutBanner.text }}
    </Message>

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

    <!-- Escolha de plano / checkout -->
    <div v-if="store.planTiers.length > 0" class="space-y-4 pt-2">
      <div>
        <h2 class="text-lg font-semibold text-text-primary dark:text-white">Escolha seu plano</h2>
        <p class="text-sm text-text-secondary">
          Quanto maior o compromisso, menor o valor mensal. Sem letras miúdas.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-3">
        <div
          v-for="tier in store.planTiers"
          :key="tier.cycle"
          class="relative rounded-lg border p-5 shadow-sm"
          :class="
            tier.cycle === 'YEARLY'
              ? 'border-2 border-primary bg-surface-light dark:bg-surface-dark'
              : 'border-black/10 bg-surface-light dark:border-white/10 dark:bg-surface-dark'
          "
        >
          <span
            v-if="tier.cycle === 'YEARLY'"
            class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white"
          >
            Mais econômico
          </span>

          <p class="text-sm font-medium text-text-secondary">{{ tier.label }}</p>
          <p class="mt-1 flex items-baseline gap-1">
            <span class="text-2xl font-bold text-text-primary dark:text-white">
              {{ formatCurrency(tier.monthlyPrice) }}
            </span>
            <span class="text-sm text-text-secondary">/mês</span>
          </p>
          <p class="mt-0.5 text-xs text-text-secondary">
            {{ formatCurrency(tier.totalPrice) }} cobrados a cada {{ tier.months }}
            {{ tier.months === 1 ? 'mês' : 'meses' }}
          </p>
          <p v-if="savingsPercent(tier)" class="mt-1.5 flex items-center gap-1 text-xs font-medium text-success">
            <Check :size="14" />
            Economize {{ savingsPercent(tier) }}% no mês
          </p>

          <Button
            :label="`Assinar ${tier.label}`"
            class="mt-4 w-full justify-center"
            :loading="store.isCheckingOut"
            @click="handleSubscribe(tier.cycle)"
          />
        </div>
      </div>

      <div
        class="flex flex-col gap-2 rounded-lg border border-black/10 p-4 text-xs text-text-secondary dark:border-white/10 sm:flex-row sm:items-center sm:justify-center sm:gap-6"
      >
        <span class="flex items-center gap-1.5">
          <ShieldCheck :size="14" class="text-primary" />
          Pagamento processado pela Asaas
        </span>
        <span class="flex items-center gap-1.5">
          <Lock :size="14" class="text-primary" />
          Pix ou Cartão de Crédito
        </span>
        <span class="flex items-center gap-1.5">
          <Clock :size="14" class="text-primary" />
          Cartão renova automaticamente; Pix gera um novo QR a cada ciclo
        </span>
      </div>
      <p class="flex items-start gap-1.5 text-xs text-text-secondary">
        <CircleAlert :size="14" class="mt-0.5 shrink-0" />
        Você será redirecionado para a página de pagamento segura da Asaas para
        concluir a assinatura.
      </p>
    </div>
  </div>
</template>
