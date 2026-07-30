<script setup lang="ts">
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import MoneyInput from '@/components/form/MoneyInput.vue'
import { type AccountReceivableFormPayload, useAccountsReceivableStore } from '@/stores/accountsReceivable'
import { useCustomersStore } from '@/stores/customers'
import { dateToIsoString, isoStringToDate } from '@/utils/date'

const store = useAccountsReceivableStore()
const customersStore = useCustomersStore()
const router = useRouter()
const toast = useToast()
const isLoading = ref(false)

const form = reactive<AccountReceivableFormPayload>({
  customerId: '',
  dueDate: '',
  amount: 0,
})

const dueDate = computed<Date | null>({
  get: () => isoStringToDate(form.dueDate),
  set: (value) => {
    form.dueDate = dateToIsoString(value)
  },
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
    toast.add({ severity: 'success', summary: 'Conta a receber criada', life: 3000 })
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
          <DatePicker
            v-model="dueDate"
            input-id="receivable-due-date"
            date-format="dd/mm/yy"
            show-icon
            icon-display="input"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label for="receivable-amount" class="text-sm font-medium text-text-primary dark:text-white">
            Valor
          </label>
          <MoneyInput id="receivable-amount" v-model="form.amount" class="w-full" />
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
