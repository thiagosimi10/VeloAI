<script setup lang="ts">
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import MoneyInput from '@/components/form/MoneyInput.vue'
import { useCategoriesStore } from '@/stores/categories'
import { type ServiceFormPayload, useServicesStore } from '@/stores/services'

const store = useServicesStore()
const categoriesStore = useCategoriesStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const serviceId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => serviceId.value !== null)
const isLoading = ref(false)

const form = reactive<ServiceFormPayload>({
  categoryId: null,
  name: '',
  description: '',
  estimatedTime: null,
  price: 0,
  active: true,
})

const categoryOptions = computed(() =>
  categoriesStore.items.map((category) => ({ label: category.name, value: category.id })),
)

const statusOptions = [
  { label: 'Ativo', value: true },
  { label: 'Inativo', value: false },
]

onMounted(async () => {
  await categoriesStore.fetchCategories({ pageSize: 100 })

  if (serviceId.value) {
    isLoading.value = true
    const service = await store.getService(serviceId.value)
    if (service) {
      form.categoryId = service.categoryId
      form.name = service.name
      form.description = service.description ?? ''
      form.estimatedTime = service.estimatedTime
      form.price = service.price
      form.active = service.active
    }
    isLoading.value = false
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result =
    isEditing.value && serviceId.value
      ? await store.updateService(serviceId.value, form)
      : await store.createService(form)
  isLoading.value = false

  if (result) {
    toast.add({
      severity: 'success',
      summary: isEditing.value ? 'Serviço atualizado' : 'Serviço criado',
      life: 3000,
    })
    await router.push({ name: 'services' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">
      {{ isEditing ? 'Editar Serviço' : 'Novo Serviço' }}
    </h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label for="service-name" class="text-sm font-medium text-text-primary dark:text-white">
          Nome
        </label>
        <InputText id="service-name" v-model="form.name" class="w-full" required />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label
            for="service-category"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Categoria
          </label>
          <Select
            v-model="form.categoryId"
            input-id="service-category"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
            show-clear
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="service-status"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Status
          </label>
          <Select
            v-model="form.active"
            input-id="service-status"
            data-testid="service-status-select"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label
            for="service-price"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Valor
          </label>
          <MoneyInput id="service-price" v-model="form.price" class="w-full" />
        </div>
        <div class="space-y-1">
          <label
            for="service-estimated-time"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Tempo Estimado (min)
          </label>
          <InputNumber
            v-model="form.estimatedTime"
            input-id="service-estimated-time"
            class="w-full"
          />
        </div>
      </div>

      <div class="space-y-1">
        <label
          for="service-description"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Descrição
        </label>
        <Textarea id="service-description" v-model="form.description" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="service-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'services' })"
        />
      </div>
    </form>
  </div>
</template>
