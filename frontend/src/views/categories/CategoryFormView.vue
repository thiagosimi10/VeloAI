<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type CategoryFormPayload, useCategoriesStore } from '@/stores/categories'

const store = useCategoriesStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const categoryId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => categoryId.value !== null)
const isLoading = ref(false)

const form = reactive<CategoryFormPayload>({
  name: '',
  description: '',
})

onMounted(async () => {
  if (categoryId.value) {
    isLoading.value = true
    const category = await store.getCategory(categoryId.value)
    if (category) {
      form.name = category.name
      form.description = category.description ?? ''
    }
    isLoading.value = false
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result =
    isEditing.value && categoryId.value
      ? await store.updateCategory(categoryId.value, form)
      : await store.createCategory(form)
  isLoading.value = false

  if (result) {
    toast.add({
      severity: 'success',
      summary: isEditing.value ? 'Categoria atualizada' : 'Categoria criada',
      life: 3000,
    })
    await router.push({ name: 'categories' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">
      {{ isEditing ? 'Editar Categoria' : 'Nova Categoria' }}
    </h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="space-y-1">
        <label for="category-name" class="text-sm font-medium text-text-primary dark:text-white">
          Nome
        </label>
        <InputText id="category-name" v-model="form.name" class="w-full" required />
      </div>

      <div class="space-y-1">
        <label
          for="category-description"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Descrição
        </label>
        <Textarea id="category-description" v-model="form.description" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="category-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'categories' })"
        />
      </div>
    </form>
  </div>
</template>
