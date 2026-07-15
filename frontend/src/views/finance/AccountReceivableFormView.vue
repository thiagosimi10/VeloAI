<script setup lang="ts">
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type AccountReceivableFormPayload, useAccountsReceivableStore } from '@/stores/accountsReceivable'
import { useCustomersStore } from '@/stores/customers'

const store = useAccountsReceivableStore()
const customersStore = useCustomersStore()
const router = useRouter()
const isLoading = ref(false)

const form = reactive<AccountReceivableFormPayload>({
  customerId: '',
  dueDate: '',
  amount: 0,
})

const customerOptions = computed(() =>
  customersStore.items.map((customer) => ({ label: customer.name, value: customer.id })),
)

onMounted(async () => {
  await customersStore.fetchCustomers({ pageSize: 100 })
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result = await store.createReceivable(form)
  isLoading.value = false

  if (result) {
    await router.push({ name: 'accounts-receivable-detail', params: { id: result.id } })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Nova Conta a Receber</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label for="receivable-customer" class="text-sm font-medium text-text-primary dark:text-white">
          Cliente
        </label>
        <Select
          v-model="form.customerId"
          input-id="receivable-customer"
          :options="customerOptions"
          option-label="label"
          option-value="value"
          filter
          class="w-full"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="receivable-due-date" class="text-sm font-medium text-text-primary dark:text-white">
            Vencimento
          </label>
          <input
            id="receivable-due-date"
            v-model="form.dueDate"
            type="date"
            class="w-full rounded-md border border-black/10 px-3 py-2 text-sm dark:border-white/10 dark:bg-transparent"
          />
        </div>
        <div class="space-y-1">
          <label for="receivable-amount" class="text-sm font-medium text-text-primary dark:text-white">
            Valor
          </label>
          <InputNumber
            v-model="form.amount"
            input-id="receivable-amount"
            mode="currency"
            currency="BRL"
            locale="pt-BR"
            class="w-full"
          />
        </div>
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Criar Conta a Receber"
          :loading="isLoading"
          data-testid="receivable-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'accounts-receivable' })"
        />
      </div>
    </form>
  </div>
</template>
