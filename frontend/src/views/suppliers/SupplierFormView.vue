<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type SupplierFormPayload, useSuppliersStore } from '@/stores/suppliers'
import { formatDocumentInput, formatPhoneInput } from '@/utils/mask'

const store = useSuppliersStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const supplierId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => supplierId.value !== null)
const isLoading = ref(false)

const form = reactive<SupplierFormPayload>({
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

const documentDisplay = computed({
  get: () => form.document,
  set: (value: string) => {
    form.document = formatDocumentInput(value)
  },
})

const phoneDisplay = computed({
  get: () => form.phone,
  set: (value: string) => {
    form.phone = formatPhoneInput(value)
  },
})

const mobileDisplay = computed({
  get: () => form.mobile,
  set: (value: string) => {
    form.mobile = formatPhoneInput(value)
  },
})

onMounted(async () => {
  if (supplierId.value) {
    isLoading.value = true
    const supplier = await store.getSupplier(supplierId.value)
    if (supplier) {
      form.type = supplier.type
      form.name = supplier.name
      form.document = formatDocumentInput(supplier.document)
      form.email = supplier.email ?? ''
      form.phone = formatPhoneInput(supplier.phone ?? '')
      form.mobile = formatPhoneInput(supplier.mobile ?? '')
      form.city = supplier.city ?? ''
      form.state = supplier.state ?? ''
      form.notes = supplier.notes ?? ''
    }
    isLoading.value = false
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result =
    isEditing.value && supplierId.value
      ? await store.updateSupplier(supplierId.value, form)
      : await store.createSupplier(form)
  isLoading.value = false

  if (result) {
    toast.add({
      severity: 'success',
      summary: isEditing.value ? 'Fornecedor atualizado' : 'Fornecedor criado',
      life: 3000,
    })
    await router.push({ name: 'suppliers' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">
      {{ isEditing ? 'Editar Fornecedor' : 'Novo Fornecedor' }}
    </h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="supplier-type" class="text-sm font-medium text-text-primary dark:text-white">
            Tipo
          </label>
          <Select
            id="supplier-type"
            v-model="form.type"
            :options="typeOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="supplier-document"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            CPF/CNPJ
          </label>
          <InputText
            id="supplier-document"
            v-model="documentDisplay"
            class="w-full"
            :disabled="isEditing"
            placeholder="000.000.000-00"
            required
          />
        </div>
      </div>

      <div class="space-y-1">
        <label for="supplier-name" class="text-sm font-medium text-text-primary dark:text-white">
          Nome
        </label>
        <InputText id="supplier-name" v-model="form.name" class="w-full" required />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="supplier-email" class="text-sm font-medium text-text-primary dark:text-white">
            E-mail
          </label>
          <InputText id="supplier-email" v-model="form.email" type="email" class="w-full" />
        </div>
        <div class="space-y-1">
          <label for="supplier-phone" class="text-sm font-medium text-text-primary dark:text-white">
            Telefone
          </label>
          <InputText
            id="supplier-phone"
            v-model="phoneDisplay"
            type="tel"
            placeholder="(00) 0000-0000"
            class="w-full"
          />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="supplier-mobile" class="text-sm font-medium text-text-primary dark:text-white">
            Celular
          </label>
          <InputText
            id="supplier-mobile"
            v-model="mobileDisplay"
            type="tel"
            placeholder="(00) 00000-0000"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label for="supplier-city" class="text-sm font-medium text-text-primary dark:text-white">
            Cidade
          </label>
          <InputText id="supplier-city" v-model="form.city" class="w-full" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="supplier-state" class="text-sm font-medium text-text-primary dark:text-white">
            Estado
          </label>
          <InputText id="supplier-state" v-model="form.state" maxlength="2" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label for="supplier-notes" class="text-sm font-medium text-text-primary dark:text-white">
          Observações
        </label>
        <Textarea id="supplier-notes" v-model="form.notes" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="supplier-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'suppliers' })"
        />
      </div>
    </form>
  </div>
</template>
