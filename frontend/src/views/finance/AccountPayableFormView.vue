<script setup lang="ts">
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type AccountPayableFormPayload, useAccountsPayableStore } from '@/stores/accountsPayable'
import { useSuppliersStore } from '@/stores/suppliers'

const store = useAccountsPayableStore()
const suppliersStore = useSuppliersStore()
const router = useRouter()
const isLoading = ref(false)

const form = reactive<AccountPayableFormPayload>({
  supplierId: '',
  dueDate: '',
  amount: 0,
})

const supplierOptions = computed(() =>
  suppliersStore.items.map((supplier) => ({ label: supplier.name, value: supplier.id })),
)

onMounted(async () => {
  await suppliersStore.fetchSuppliers({ pageSize: 100 })
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result = await store.createPayable(form)
  isLoading.value = false

  if (result) {
    await router.push({ name: 'accounts-payable-detail', params: { id: result.id } })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Nova Conta a Pagar</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label for="payable-supplier" class="text-sm font-medium text-text-primary dark:text-white">
          Fornecedor
        </label>
        <Select
          v-model="form.supplierId"
          input-id="payable-supplier"
          :options="supplierOptions"
          option-label="label"
          option-value="value"
          filter
          class="w-full"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="payable-due-date" class="text-sm font-medium text-text-primary dark:text-white">
            Vencimento
          </label>
          <input
            id="payable-due-date"
            v-model="form.dueDate"
            type="date"
            class="w-full rounded-md border border-black/10 px-3 py-2 text-sm dark:border-white/10 dark:bg-transparent"
          />
        </div>
        <div class="space-y-1">
          <label for="payable-amount" class="text-sm font-medium text-text-primary dark:text-white">
            Valor
          </label>
          <InputNumber
            v-model="form.amount"
            input-id="payable-amount"
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
          label="Criar Conta a Pagar"
          :loading="isLoading"
          data-testid="payable-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'accounts-payable' })"
        />
      </div>
    </form>
  </div>
</template>
