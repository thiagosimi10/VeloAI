<script setup lang="ts">
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import MoneyInput from '@/components/form/MoneyInput.vue'
import { useCustomersStore } from '@/stores/customers'
import { useProductsStore } from '@/stores/products'
import { type Sale, type SaleStatus, useSalesStore } from '@/stores/sales'

const store = useSalesStore()
const customersStore = useCustomersStore()
const productsStore = useProductsStore()
const route = useRoute()
const router = useRouter()
const confirm = useConfirm()
const toast = useToast()

const saleId = computed(() => route.params.id as string)
const sale = ref<Sale | null>(null)
const actionError = ref<string | null>(null)

const statusLabels: Record<SaleStatus, string> = {
  open: 'Aberta',
  paid: 'Paga',
  cancelled: 'Cancelada',
}

const paymentMethodLabels: Record<string, string> = {
  pix: 'PIX',
  dinheiro: 'Dinheiro',
  cartao_credito: 'Cartão Crédito',
  cartao_debito: 'Cartão Débito',
  transferencia: 'Transferência',
}

const itemForm = reactive({
  productId: '',
  quantity: 1,
  unitPrice: null as number | null,
})

const discountForm = reactive({
  discount: 0,
})

const productOptions = computed(() =>
  productsStore.items.map((product) => ({ label: `${product.name} (${product.sku})`, value: product.id })),
)

const customerName = computed(() => {
  const customer = customersStore.items.find((item) => item.id === sale.value?.customerId)
  return customer?.name ?? sale.value?.customerId ?? '—'
})

function productName(productId: string): string {
  return productsStore.items.find((product) => product.id === productId)?.name ?? productId
}

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

const canEdit = computed(() => sale.value?.status === 'open')

async function loadData(): Promise<void> {
  sale.value = await store.getSale(saleId.value)
  if (sale.value) {
    discountForm.discount = sale.value.discount
  }
}

onMounted(async () => {
  await Promise.all([
    loadData(),
    customersStore.fetchCustomers({ pageSize: 100 }),
    productsStore.fetchProducts(),
  ])
})

async function handleAddItem(): Promise<void> {
  actionError.value = null
  if (!itemForm.productId) {
    actionError.value = 'Selecione um produto.'
    return
  }
  const result = await store.addItem(saleId.value, {
    productId: itemForm.productId,
    quantity: itemForm.quantity,
    unitPrice: itemForm.unitPrice,
  })
  if (result) {
    itemForm.productId = ''
    itemForm.quantity = 1
    itemForm.unitPrice = null
    await loadData()
  }
}

function handleRemoveItem(itemId: string): void {
  confirm.require({
    header: 'Remover item',
    message: 'Remover este item da Venda?',
    acceptProps: { label: 'Remover', severity: 'danger' },
    rejectProps: { label: 'Cancelar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const success = await store.removeItem(saleId.value, itemId)
      if (success) {
        toast.add({ severity: 'success', summary: 'Item removido', life: 3000 })
        await loadData()
      }
    },
  })
}

async function handleApplyDiscount(): Promise<void> {
  const result = await store.updateSale(saleId.value, {
    discount: discountForm.discount,
    paymentMethod: sale.value?.paymentMethod,
  })
  if (result) {
    sale.value = result
    toast.add({ severity: 'success', summary: 'Desconto aplicado', life: 3000 })
  }
}

async function handleComplete(): Promise<void> {
  const result = await store.completeSale(saleId.value)
  if (result) {
    sale.value = result
    await productsStore.fetchProducts()
    toast.add({ severity: 'success', summary: 'Venda concluída', life: 3000 })
  }
}

function handleCancel(): void {
  confirm.require({
    header: 'Cancelar venda',
    message: 'Cancelar esta Venda? Esta ação não pode ser desfeita.',
    acceptProps: { label: 'Cancelar Venda', severity: 'danger' },
    rejectProps: { label: 'Voltar', severity: 'secondary', variant: 'outlined' },
    accept: async () => {
      const result = await store.cancelSale(saleId.value)
      if (result) {
        sale.value = result
        toast.add({ severity: 'success', summary: 'Venda cancelada', life: 3000 })
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
      @click="router.push({ name: 'sales' })"
    >
      ← Voltar para Vendas
    </button>

    <template v-if="sale">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">Venda</h1>
        <span class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
          {{ statusLabels[sale.status] }}
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
          <p class="text-xs text-text-secondary">Forma de Pagamento</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ sale.paymentMethod ? paymentMethodLabels[sale.paymentMethod] ?? sale.paymentMethod : '—' }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Desconto</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(sale.discount) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Total</p>
          <p class="text-sm font-medium text-text-primary dark:text-white">
            {{ formatCurrency(sale.total) }}
          </p>
        </div>
      </div>

      <div
        v-if="canEdit"
        class="flex flex-wrap items-end gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <div class="space-y-1">
          <label class="text-sm font-medium text-text-primary dark:text-white">Desconto</label>
          <MoneyInput v-model="discountForm.discount" class="w-40" />
        </div>
        <Button type="button" label="Aplicar Desconto" severity="secondary" @click="handleApplyDiscount" />
      </div>

      <div class="space-y-2">
        <h2 class="text-sm font-semibold text-text-primary dark:text-white">Itens</h2>
        <div class="overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
          <table class="w-full text-left text-sm">
            <thead class="bg-black/5 dark:bg-white/5">
              <tr>
                <th class="px-4 py-2 font-medium text-text-secondary">Produto</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Quantidade</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Preço Unit.</th>
                <th class="px-4 py-2 font-medium text-text-secondary">Total</th>
                <th v-if="canEdit" class="px-4 py-2 font-medium text-text-secondary">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="sale.items.length === 0">
                <td colspan="5" class="px-4 py-6 text-center text-text-secondary">
                  Nenhum item adicionado.
                </td>
              </tr>
              <tr
                v-for="item in sale.items"
                :key="item.id"
                class="border-t border-black/5 dark:border-white/10"
              >
                <td class="px-4 py-2">{{ productName(item.productId) }}</td>
                <td class="px-4 py-2">{{ item.quantity }}</td>
                <td class="px-4 py-2">{{ formatCurrency(item.unitPrice) }}</td>
                <td class="px-4 py-2">{{ formatCurrency(item.total) }}</td>
                <td v-if="canEdit" class="px-4 py-2">
                  <button
                    type="button"
                    aria-label="Remover item"
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
          v-if="canEdit"
          class="grid grid-cols-1 gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10 sm:grid-cols-4"
          @submit.prevent="handleAddItem"
        >
          <Select
            v-model="itemForm.productId"
            :options="productOptions"
            option-label="label"
            option-value="value"
            filter
            placeholder="Selecione um produto"
            class="w-full sm:col-span-2"
          />
          <InputNumber v-model="itemForm.quantity" :min="1" placeholder="Qtd." class="w-full" />
          <Button type="submit" label="Adicionar Item" data-testid="add-item-submit" />
        </form>
      </div>

      <div
        v-if="canEdit"
        class="flex flex-wrap items-end gap-3 rounded-lg border border-black/10 p-4 dark:border-white/10"
      >
        <Button type="button" label="Concluir Venda" data-testid="complete-sale-button" @click="handleComplete" />
        <Button
          type="button"
          label="Cancelar Venda"
          severity="secondary"
          data-testid="cancel-sale-button"
          @click="handleCancel"
        />
      </div>
    </template>
    <p v-else class="text-sm text-text-secondary">Carregando...</p>
  </div>
</template>
