<script setup lang="ts">
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AttachmentsPanel from '@/components/AttachmentsPanel.vue'
import { useCustomersStore } from '@/stores/customers'
import { useProductsStore } from '@/stores/products'
import { type ServiceOrder, type ServiceOrderStatus, useServiceOrdersStore } from '@/stores/serviceOrders'
import { useServicesStore } from '@/stores/services'
import { useUsersStore } from '@/stores/users'

const store = useServiceOrdersStore()
const customersStore = useCustomersStore()
const usersStore = useUsersStore()
const productsStore = useProductsStore()
const servicesStore = useServicesStore()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const toast = useToast()

const orderId = computed(() => route.params.id as string)
const order = ref<ServiceOrder | null>(null)
const actionError = ref<string | null>(null)

const statusLabels: Record<ServiceOrderStatus, string> = {
  open: 'Aberta',
  in_progress: 'Em Atendimento',
  completed: 'Concluída',
  cancelled: 'Cancelada',
}

const itemTypeOptions = [
  { label: 'Produto', value: 'product' },
  { label: 'Serviço', value: 'service' },
]

const itemForm = reactive({
  type: 'product' as 'product' | 'service',
  referenceId: '',
  quantity: 1,
  unitPrice: null as number | null,
})

const closeForm = reactive({
  technicianId: null as string | null,
  solution: '',
})

const productOptions = computed(() =>
  productsStore.items.map((product) => ({ label: `${product.name} (${product.sku})`, value: product.id })),
)
const serviceOptions = computed(() =>
  servicesStore.items.map((service) => ({ label: service.name, value: service.id })),
)
const technicianOptions = computed(() =>
  usersStore.items.map((user) => ({
    label: user.lastName ? `${user.firstName} ${user.lastName}` : user.firstName,
    value: user.id,
  })),
)

const customerName = computed(() => {
  const customer = customersStore.items.find((item) => item.id === order.value?.customerId)
  return customer?.name ?? order.value?.customerId ?? '—'
})

function technicianName(technicianId: string | null): string {
  if (!technicianId) return '—'
  const user = usersStore.items.find((item) => item.id === technicianId)
  if (!user) return technicianId
  return user.lastName ? `${user.firstName} ${user.lastName}` : user.firstName
}

function referenceName(item: { productId: string | null; serviceId: string | null }): string {
  if (item.productId) {
    return productsStore.items.find((product) => product.id === item.productId)?.name ?? item.productId
  }
  return servicesStore.items.find((service) => service.id === item.serviceId)?.name ?? item.serviceId ?? '—'
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const canEditItems = computed(
  () => order.value?.status === 'open' || order.value?.status === 'in_progress',
)
const canStart = computed(() => order.value?.status === 'open')
const canCloseOrCancel = computed(
  () => order.value?.status === 'open' || order.value?.status === 'in_progress',
)

async function loadData(): Promise<void> {
  order.value = await store.getOrder(orderId.value)
  if (order.value) {
    closeForm.technicianId = order.value.technicianId
  }
}

onMounted(async () => {
  await Promise.all([
    loadData(),
    customersStore.fetchCustomers({ pageSize: 100 }),
    usersStore.fetchUsers({ pageSize: 100 }),
    productsStore.fetchProducts(),
    servicesStore.fetchServices(),
  ])
})

async function handleAddItem(): Promise<void> {
  actionError.value = null
  if (!itemForm.referenceId) {
    actionError.value = 'Selecione um produto ou serviço.'
    return
  }
  const result = await store.addItem(orderId.value, {
    productId: itemForm.type === 'product' ? itemForm.referenceId : null,
    serviceId: itemForm.type === 'service' ? itemForm.referenceId : null,
    quantity: itemForm.quantity,
    unitPrice: itemForm.unitPrice,
  })
  if (result) {
    itemForm.referenceId = ''
    itemForm.quantity = 1
    itemForm.unitPrice = null
    await loadData()
  }
}

function handleRemoveItem(itemId: string): void {
  confirm.require({
    header: 'Remover item',
    message: 'Remover este item da Ordem de Serviço?',
    acceptProps: { label: 'Remover', severity: 'danger' },
    rejectProps: { label: 'Cancelar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const success = await store.removeItem(orderId.value, itemId)
      if (success) {
        toast.add({ severity: 'success', summary: 'Item removido', life: 3000 })
        await loadData()
      }
    },
  })
}

async function handleStart(): Promise<void> {
  const result = await store.startOrder(orderId.value)
  if (result) {
    order.value = result
    toast.add({ severity: 'success', summary: 'Ordem de serviço iniciada', life: 3000 })
  }
}

async function handleClose(): Promise<void> {
  const result = await store.closeOrder(orderId.value, {
    technicianId: closeForm.technicianId,
    solution: closeForm.solution || null,
  })
  if (result) {
    order.value = result
    await productsStore.fetchProducts()
    toast.add({ severity: 'success', summary: 'Ordem de serviço concluída', life: 3000 })
  }
}

function handleCancel(): void {
  confirm.require({
    header: 'Cancelar ordem de serviço',
    message: 'Cancelar esta Ordem de Serviço? Esta ação não pode ser desfeita.',
    acceptProps: { label: 'Cancelar OS', severity: 'danger' },
    rejectProps: { label: 'Voltar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const result = await store.cancelOrder(orderId.value)
      if (result) {
        order.value = result
        toast.add({ severity: 'success', summary: 'Ordem de serviço cancelada', life: 3000 })
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
      @click="router.push({ name: 'service-orders' })"
    >
      ← Voltar para Ordens de Serviço
    </button>

    <template v-if="order">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">
          {{ order.number }}
        </h1>
        <span class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
          {{ statusLabels[order.status] }}
        </span>
      </div>

      <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>
      <Message v-if="actionError" severity="warn" :closable="false">{{ actionError }}</Message>

      <div class="grid grid-cols-2 gap-4 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-4">
        <div>
          <p class="text-xs text-text-secondary">Cliente</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">{{ customerName }}</p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Técnico</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ technicianName(order.technicianId) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Equipamento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ order.equipment ?? '—' }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Total</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(order.total) }}
          </p>
        </div>
      </div>

      <div v-if="order.problem" class="rounded-lg border border-black/10 p-4 dark:border-white/10">
        <p class="text-xs text-text-secondary">Problema Informado</p>
        <p class="text-sm text-text-primary dark:text-white">{{ order.problem }}</p>
      </div>

      <div class="space-y-2">
        <h2 class="text-sm font-semibold text-text-primary dark:text-white">Itens</h2>
        <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
          <table class="w-full text-left text-sm">
            <thead class="bg-black/5 dark:bg-white/5">
              <tr>
                <th class="px-4 py-2 font-medium text-text-secondary">Item</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Quantidade</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Preço Unit.</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Total</th>
                <th v-if="canEditItems" class="px-4 py-2 font-medium text-text-secondary">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="order.items.length === 0">
                <td colspan="5" class="px-4 py-6 text-center text-text-secondary">
                  Nenhum item adicionado.
                </td>
              </tr>
              <tr
                v-for="item in order.items"
                :key="item.id"
                class="border-t border-black/5 dark:border-white/10"
              >
                <td class="px-4 py-2">{{ referenceName(item) }}</td>
                <td class="px-4 py-2">{{ item.quantity }}</td>
                <td class="px-4 py-2">{{ formatCurrency(item.unitPrice) }}</td>
                <td class="px-4 py-2">{{ formatCurrency(item.total) }}</td>
                <td v-if="canEditItems" class="px-4 py-2">
                  <button
                    type="button"
                    :aria-label="`Remover item`"
                    class="text-text-secondary hover:text-danger"
                    @click="handleRemoveItem(item.id)"
                  >
                    Remover
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <form
          v-if="canEditItems"
          class="grid grid-cols-1 gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-5"
          @submit.prevent="handleAddItem"
        >
          <Select
            v-model="itemForm.type"
            :options="itemTypeOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            @update:model-value="itemForm.referenceId = ''"
          />
          <Select
            v-if="itemForm.type === 'product'"
            v-model="itemForm.referenceId"
            :options="productOptions"
            option-label="label"
            option-value="value"
            filter
            placeholder="Selecione um produto"
            class="w-full sm:col-span-2"
          />
          <Select
            v-else
            v-model="itemForm.referenceId"
            :options="serviceOptions"
            option-label="label"
            option-value="value"
            filter
            placeholder="Selecione um serviço"
            class="w-full sm:col-span-2"
          />
          <InputNumber v-model="itemForm.quantity" :min="1" placeholder="Qtd." class="w-full" />
          <Button type="submit" label="Adicionar Item" data-testid="add-item-submit" />
        </form>
      </div>

      <div
        v-if="canStart || canCloseOrCancel"
        class="flex flex-wrap items-end gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <Button
          v-if="canStart"
          type="button"
          label="Iniciar Atendimento"
          data-testid="start-order-button"
          @click="handleStart"
        />

        <template v-if="order.status === 'in_progress'">
          <div class="space-y-1">
            <label class="text-sm font-medium text-text-primary dark:text-white">Técnico</label>
            <Select
              v-model="closeForm.technicianId"
              :options="technicianOptions"
              option-label="label"
              option-value="value"
              show-clear
              class="w-56"
            />
          </div>
          <div class="min-w-[200px] flex-1 space-y-1">
            <label class="text-sm font-medium text-text-primary dark:text-white">Solução</label>
            <Textarea v-model="closeForm.solution" class="w-full" rows="1" />
          </div>
          <Button
            type="button"
            label="Concluir OS"
            data-testid="close-order-button"
            @click="handleClose"
          />
        </template>

        <Button
          v-if="canCloseOrCancel"
          type="button"
          label="Cancelar OS"
          severity="secondary"
          data-testid="cancel-order-button"
          @click="handleCancel"
        />
      </div>

      <AttachmentsPanel resource-type="service_order" :resource-id="orderId" />
    </template>
    <p v-else class="text-sm text-text-secondary">Carregando...</p>
  </div>
</template>
