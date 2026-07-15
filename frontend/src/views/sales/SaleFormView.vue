<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useCustomersStore } from '@/stores/customers'
import { type SaleFormPayload, useSalesStore } from '@/stores/sales'

const store = useSalesStore()
const customersStore = useCustomersStore()
const router = useRouter()
const isLoading = ref(false)

const form = reactive<SaleFormPayload>({
  customerId: '',
  paymentMethod: null,
})

const paymentMethodOptions = [
  { label: 'PIX', value: 'pix' },
  { label: 'Dinheiro', value: 'dinheiro' },
  { label: 'Cartão Crédito', value: 'cartao_credito' },
  { label: 'Cartão Débito', value: 'cartao_debito' },
  { label: 'Transferência', value: 'transferencia' },
]

const customerOptions = computed(() =>
  customersStore.items.map((customer) => ({ label: customer.name, value: customer.id })),
)

onMounted(async () => {
  await customersStore.fetchCustomers({ pageSize: 100 })
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result = await store.createSale(form)
  isLoading.value = false

  if (result) {
    await router.push({ name: 'sales-detail', params: { id: result.id } })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Nova Venda</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="sale-customer" class="text-sm font-medium text-text-primary dark:text-white">
            Cliente
          </label>
          <Select
            v-model="form.customerId"
            input-id="sale-customer"
            :options="customerOptions"
            option-label="label"
            option-value="value"
            filter
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="sale-payment-method"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Forma de Pagamento
          </label>
          <Select
            v-model="form.paymentMethod"
            input-id="sale-payment-method"
            :options="paymentMethodOptions"
            option-label="label"
            option-value="value"
            show-clear
            class="w-full"
          />
        </div>
      </div>

      <div class="flex gap-2">
        <Button type="submit" label="Criar Venda" :loading="isLoading" data-testid="sale-form-submit" />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'sales' })"
        />
      </div>
    </form>
  </div>
</template>
