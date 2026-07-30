<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type AccountReceivable, useAccountsReceivableStore } from '@/stores/accountsReceivable'
import { useCustomersStore } from '@/stores/customers'

const store = useAccountsReceivableStore()
const customersStore = useCustomersStore()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const toast = useToast()

const receivableId = computed(() => route.params.id as string)
const receivable = ref<AccountReceivable | null>(null)

const statusLabels = {
  pending: 'Pendente',
  received: 'Recebida',
  cancelled: 'Cancelada',
} as const

const customerName = computed(() => {
  const customer = customersStore.items.find((item) => item.id === receivable.value?.customerId)
  return customer?.name ?? receivable.value?.customerId ?? '—'
})

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('pt-BR')
}

const canAct = computed(() => receivable.value?.status === 'pending')

async function loadData(): Promise<void> {
  receivable.value = await store.getReceivable(receivableId.value)
}

onMounted(async () => {
  await Promise.all([loadData(), customersStore.fetchCustomers({ pageSize: 100 })])
})

async function handleReceive(): Promise<void> {
  const result = await store.receiveReceivable(receivableId.value)
  if (result) {
    receivable.value = result
    toast.add({ severity: 'success', summary: 'Conta marcada como recebida', life: 3000 })
  }
}

function handleCancel(): void {
  confirm.require({
    header: 'Cancelar conta a receber',
    message: 'Cancelar esta Conta a Receber? Esta ação não pode ser desfeita.',
    acceptProps: { label: 'Cancelar Conta', severity: 'danger' },
    rejectProps: { label: 'Voltar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const result = await store.cancelReceivable(receivableId.value)
      if (result) {
        receivable.value = result
        toast.add({ severity: 'success', summary: 'Conta a receber cancelada', life: 3000 })
      }
    },
  })
}
</script>

<template>
  <div class="space-y-5">
    <button
      type="button"
      class="text-sm text-text-secondary hover:text-primary"
      @click="router.push({ name: 'accounts-receivable' })"
    >
      ← Voltar para Contas a Receber
    </button>

    <template v-if="receivable">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">Conta a Receber</h1>
        <span class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
          {{ statusLabels[receivable.status] }}
          <template v-if="receivable.isOverdue"> (Vencida)</template>
        </span>
      </div>

      <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

      <div class="grid grid-cols-2 gap-4 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-4">
        <div>
          <p class="text-xs text-text-secondary">Cliente</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">{{ customerName }}</p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Vencimento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatDate(receivable.dueDate) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Valor</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(receivable.amount) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Data de Recebimento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ receivable.paymentDate ? formatDate(receivable.paymentDate) : '—' }}
          </p>
        </div>
      </div>

      <div
        v-if="canAct"
        class="flex flex-wrap gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <Button label="Receber" data-testid="receive-button" @click="handleReceive" />
        <Button
          label="Cancelar Conta"
          severity="secondary"
          data-testid="cancel-receivable-button"
          @click="handleCancel"
        />
      </div>
    </template>
    <p v-else class="text-sm text-text-secondary">Carregando...</p>
  </div>
</template>
