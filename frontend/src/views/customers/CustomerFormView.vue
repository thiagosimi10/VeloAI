<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type CustomerFormPayload, useCustomersStore } from '@/stores/customers'

const store = useCustomersStore()
const route = useRoute()
const router = useRouter()

const customerId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => customerId.value !== null)
const isLoading = ref(false)

const form = reactive<CustomerFormPayload>({
  type: 'PF',
  name: '',
  document: '',
  email: '',
  phone: '',
  mobile: '',
  city: '',
  state: '',
  notes: '',
})

const typeOptions = [
  { label: 'Pessoa Física', value: 'PF' },
  { label: 'Pessoa Jurídica', value: 'PJ' },
]

onMounted(async () => {
  if (customerId.value) {
    isLoading.value = true
    const customer = await store.getCustomer(customerId.value)
    if (customer) {
      form.type = customer.type
      form.name = customer.name
      form.document = customer.document
      form.email = customer.email ?? ''
      form.phone = customer.phone ?? ''
      form.mobile = customer.mobile ?? ''
      form.city = customer.city ?? ''
      form.state = customer.state ?? ''
      form.notes = customer.notes ?? ''
    }
    isLoading.value = false
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result =
    isEditing.value && customerId.value
      ? await store.updateCustomer(customerId.value, form)
      : await store.createCustomer(form)
  isLoading.value = false

  if (result) {
    await router.push({ name: 'customers' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">
      {{ isEditing ? 'Editar Cliente' : 'Novo Cliente' }}
    </h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="customer-type" class="text-sm font-medium text-text-primary dark:text-white">
            Tipo
          </label>
          <Select
            id="customer-type"
            v-model="form.type"
            :options="typeOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="customer-document"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            CPF/CNPJ
          </label>
          <InputText
            id="customer-document"
            v-model="form.document"
            class="w-full"
            :disabled="isEditing"
            required
          />
        </div>
      </div>

      <div class="space-y-1">
        <label for="customer-name" class="text-sm font-medium text-text-primary dark:text-white">
          Nome
        </label>
        <InputText id="customer-name" v-model="form.name" class="w-full" required />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="customer-email" class="text-sm font-medium text-text-primary dark:text-white">
            E-mail
          </label>
          <InputText id="customer-email" v-model="form.email" type="email" class="w-full" />
        </div>
        <div class="space-y-1">
          <label for="customer-phone" class="text-sm font-medium text-text-primary dark:text-white">
            Telefone
          </label>
          <InputText id="customer-phone" v-model="form.phone" class="w-full" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="customer-city" class="text-sm font-medium text-text-primary dark:text-white">
            Cidade
          </label>
          <InputText id="customer-city" v-model="form.city" class="w-full" />
        </div>
        <div class="space-y-1">
          <label for="customer-state" class="text-sm font-medium text-text-primary dark:text-white">
            Estado
          </label>
          <InputText id="customer-state" v-model="form.state" maxlength="2" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label for="customer-notes" class="text-sm font-medium text-text-primary dark:text-white">
          Observações
        </label>
        <Textarea id="customer-notes" v-model="form.notes" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="customer-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'customers' })"
        />
      </div>
    </form>
  </div>
</template>
