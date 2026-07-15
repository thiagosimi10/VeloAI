<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type AccountPayable, useAccountsPayableStore } from '@/stores/accountsPayable'
import { useSuppliersStore } from '@/stores/suppliers'

const store = useAccountsPayableStore()
const suppliersStore = useSuppliersStore()
const route = useRoute()
const router = useRouter()

const payableId = computed(() => route.params.id as string)
const payable = ref<AccountPayable | null>(null)

const statusLabels = {
  pending: 'Pendente',
  paid: 'Paga',
  cancelled: 'Cancelada',
} as const

const supplierName = computed(() => {
  const supplier = suppliersStore.items.find((item) => item.id === payable.value?.supplierId)
  return supplier?.name ?? payable.value?.supplierId ?? '—'
})

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

const canAct = computed(() => payable.value?.status === 'pending')

async function loadData(): Promise<void> {
  payable.value = await store.getPayable(payableId.value)
}

onMounted(async () => {
  await Promise.all([loadData(), suppliersStore.fetchSuppliers({ pageSize: 100 })])
})

async function handlePay(): Promise<void> {
  const result = await store.payPayable(payableId.value)
  if (result) {
    payable.value = result
  }
}

async function handleCancel(): Promise<void> {
  if (!window.confirm('Cancelar esta Conta a Pagar?')) {
    return
  }
  const result = await store.cancelPayable(payableId.value)
  if (result) {
    payable.value = result
  }
}
</script>

<template>
  <div class="space-y-5">
    <button
      type="button"
      class="text-sm text-text-secondary hover:text-primary"
      @click="router.push({ name: 'accounts-payable' })"
    >
      ← Voltar para Contas a Pagar
    </button>

    <template v-if="payable">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">Conta a Pagar</h1>
        <span class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
          {{ statusLabels[payable.status] }}
          <template v-if="payable.isOverdue"> (Vencida)</template>
        </span>
      </div>

      <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

      <div class="grid grid-cols-2 gap-4 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-4">
        <div>
          <p class="text-xs text-text-secondary">Fornecedor</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">{{ supplierName }}</p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Vencimento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatDate(payable.dueDate) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Valor</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(payable.amount) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Data de Pagamento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ payable.paymentDate ? formatDate(payable.paymentDate) : '—' }}
          </p>
        </div>
      </div>

      <div
        v-if="canAct"
        class="flex flex-wrap gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <Button label="Pagar" data-testid="pay-button" @click="handlePay" />
        <Button
          label="Cancelar Conta"
          severity="secondary"
          data-testid="cancel-payable-button"
          @click="handleCancel"
        />
      </div>
    </template>
    <p v-else class="text-sm text-text-secondary">Carregando...</p>
  </div>
</template>
