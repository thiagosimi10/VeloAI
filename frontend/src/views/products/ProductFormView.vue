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
import { type ProductFormPayload, useProductsStore } from '@/stores/products'
import { useSuppliersStore } from '@/stores/suppliers'

const store = useProductsStore()
const categoriesStore = useCategoriesStore()
const suppliersStore = useSuppliersStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const productId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => productId.value !== null)
const isLoading = ref(false)

const form = reactive<ProductFormPayload>({
  categoryId: null,
  supplierId: null,
  sku: '',
  barcode: '',
  name: '',
  description: '',
  costPrice: 0,
  salePrice: 0,
  stock: 0,
  minimumStock: null,
  maximumStock: null,
  unit: 'UN',
  weight: null,
})

const categoryOptions = computed(() =>
  categoriesStore.items.map((category) => ({ label: category.name, value: category.id })),
)
const supplierOptions = computed(() =>
  suppliersStore.items.map((supplier) => ({ label: supplier.name, value: supplier.id })),
)

const previewMargin = computed(() => form.salePrice - form.costPrice)

onMounted(async () => {
  await Promise.all([
    categoriesStore.fetchCategories({ pageSize: 100 }),
    suppliersStore.fetchSuppliers({ pageSize: 100 }),
  ])

  if (productId.value) {
    isLoading.value = true
    const product = await store.getProduct(productId.value)
    if (product) {
      form.categoryId = product.categoryId
      form.supplierId = product.supplierId
      form.sku = product.sku
      form.barcode = product.barcode ?? ''
      form.name = product.name
      form.description = product.description ?? ''
      form.costPrice = product.costPrice
      form.salePrice = product.salePrice
      form.stock = product.stock
      form.minimumStock = product.minimumStock
      form.maximumStock = product.maximumStock
      form.unit = product.unit
      form.weight = product.weight
    }
    isLoading.value = false
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true
  const result =
    isEditing.value && productId.value
      ? await store.updateProduct(productId.value, form)
      : await store.createProduct(form)
  isLoading.value = false

  if (result) {
    toast.add({
      severity: 'success',
      summary: isEditing.value ? 'Produto atualizado' : 'Produto criado',
      life: 3000,
    })
    await router.push({ name: 'products' })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">
      {{ isEditing ? 'Editar Produto' : 'Novo Produto' }}
    </h1>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="product-sku" class="text-sm font-medium text-text-primary dark:text-white">
            SKU
          </label>
          <InputText
            id="product-sku"
            v-model="form.sku"
            class="w-full"
            :disabled="isEditing"
            required
          />
        </div>
        <div class="space-y-1">
          <label
            for="product-barcode"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Código de Barras
          </label>
          <InputText id="product-barcode" v-model="form.barcode" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label for="product-name" class="text-sm font-medium text-text-primary dark:text-white">
          Nome
        </label>
        <InputText id="product-name" v-model="form.name" class="w-full" required />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label
            for="product-category"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Categoria
          </label>
          <Select
            v-model="form.categoryId"
            input-id="product-category"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
            show-clear
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label
            for="product-supplier"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Fornecedor
          </label>
          <Select
            v-model="form.supplierId"
            input-id="product-supplier"
            :options="supplierOptions"
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
            for="product-cost-price"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Preço de Custo
          </label>
          <MoneyInput id="product-cost-price" v-model="form.costPrice" class="w-full" />
        </div>
        <div class="space-y-1">
          <label
            for="product-sale-price"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Preço de Venda
          </label>
          <MoneyInput id="product-sale-price" v-model="form.salePrice" class="w-full" />
        </div>
      </div>

      <p class="text-sm text-text-secondary">
        Margem estimada:
        <span class="font-medium text-text-primary dark:text-white">
          {{ previewMargin.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
        </span>
      </p>

      <div class="grid grid-cols-3 gap-4">
        <div class="space-y-1">
          <label
            for="product-stock"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Estoque
          </label>
          <InputNumber v-model="form.stock" input-id="product-stock" class="w-full" />
        </div>
        <div class="space-y-1">
          <label
            for="product-minimum-stock"
            class="text-sm font-medium text-text-primary dark:text-white"
          >
            Estoque Mínimo
          </label>
          <InputNumber
            v-model="form.minimumStock"
            input-id="product-minimum-stock"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <label for="product-unit" class="text-sm font-medium text-text-primary dark:text-white">
            Unidade
          </label>
          <InputText id="product-unit" v-model="form.unit" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label
          for="product-description"
          class="text-sm font-medium text-text-primary dark:text-white"
        >
          Descrição
        </label>
        <Textarea id="product-description" v-model="form.description" class="w-full" rows="3" />
      </div>

      <div class="flex gap-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="product-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'products' })"
        />
      </div>
    </form>
  </div>
</template>
