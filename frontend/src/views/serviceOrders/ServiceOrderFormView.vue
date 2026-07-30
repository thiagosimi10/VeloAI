<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useCustomersStore } from '@/stores/customers'
import { type ServiceOrderFormPayload, useServiceOrdersStore } from '@/stores/serviceOrders'
import { useUsersStore } from '@/stores/users'

const store = useServiceOrdersStore()
const customersStore = useCustomersStore()
const usersStore = useUsersStore()
const router = useRouter()
const toast = useToast()
const isLoading = ref(false)

const form = reactive<ServiceOrderFormPayload>({
  customerId: '',
  technicianId: null,
  equipment: '',
  serialNumber: '',
  problem: '',
})

const customerOptions = computed(() =>
  customersStore.items.map((customer) => ({ label: customer.name, value: customer.id })),
)
const technicianOptions = computed(() =>
  usersStore.items.map((user) => ({
    label: user.lastName ? `${user.firstName} ${user.lastName}` : user.firstName,
    value: user.id,
  })),
)

onMounted(async () => {
  await Promise.all([
    customersStore.fetchCustomers({ pageSize: 100 }),
    usersStore.fetchUsers({ pageSize: 100 }),
  ])
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result = await store.createOrder(form)
  isLoading.value = false

  if (result) {
    toast.add({ severity: 'success', summary: 'Ordem de serviço criada', life: 3000 })
    await router.push({ name: 'service-orders-detail', params: { id: result.id } })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Nova Ordem de Serviço</h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label
            for="service-order-customer"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Cliente
          </label>
          <Select
            v-model="form.customerId"
            input-id="service-order-customer"
            :options="customerOptions"
            option-label="label"
            option-value="value"
            filter
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="service-order-technician"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Técnico Responsável
          </label>
          <Select
            v-model="form.technicianId"
            input-id="service-order-technician"
            :options="technicianOptions"
            option-label="label"
            option-value="value"
            show-clear
            class="w-full"
          />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label
            for="service-order-equipment"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Equipamento
          </label>
          <InputText id="service-order-equipment" v-model="form.equipment" class="w-full" />
        </div>
        <div class="space-y-1">
          <label
            for="service-order-serial-number"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Número de Série
          </label>
          <InputText
            id="service-order-serial-number"
            v-model="form.serialNumber"
            class="w-full"
          />
        </div>
      </div>

      <div class="space-y-1">
        <label
          for="service-order-problem"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Problema Informado
        </label>
        <Textarea id="service-order-problem" v-model="form.problem" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Criar OS"
          :loading="isLoading"
          data-testid="service-order-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'service-orders' })"
        />
      </div>
    </form>
  </div>
</template>
