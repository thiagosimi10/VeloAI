<script setup lang="ts">
import { Building2 } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { onMounted, reactive, ref, watch } from 'vue'

import { useCompanyStore } from '@/stores/company'

const store = useCompanyStore()
const toast = useToast()
const isSaving = ref(false)

const form = reactive({
  legalName: '',
  tradeName: '',
  email: '',
  phone: '',
})

watch(
  () => store.company,
  (company) => {
    if (!company) return
    form.legalName = company.legalName
    form.tradeName = company.tradeName ?? ''
    form.email = company.email ?? ''
    form.phone = company.phone ?? ''
  },
  { immediate: true },
)

onMounted(() => {
  void store.fetchCompany()
})

async function handleSubmit(): Promise<void> {
  isSaving.value = true
  const success = await store.updateCompany({
    legalName: form.legalName,
    tradeName: form.tradeName || null,
    email: form.email || null,
    phone: form.phone || null,
  })
  isSaving.value = false

  if (success) {
    toast.add({ severity: 'success', summary: 'Empresa atualizada', life: 3000 })
  }
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <div class="flex items-center gap-2">
      <Building2 :size="22" class="text-primary" />
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">
        Configurações da Empresa
      </h1>
    </div>

    <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

    <form
      class="space-y-4 rounded-xl border border-black/5 bg-surface-light p-5 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      @submit.prevent="handleSubmit"
    >
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="company-legal-name" class="text-sm font-medium text-text-primary dark:text-white">
            Razão Social
          </label>
          <InputText id="company-legal-name" v-model="form.legalName" class="w-full" required />
        </div>
        <div class="space-y-1">
          <label for="company-trade-name" class="text-sm font-medium text-text-primary dark:text-white">
            Nome Fantasia
          </label>
          <InputText id="company-trade-name" v-model="form.tradeName" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label class="text-sm font-medium text-text-primary dark:text-white">CNPJ/CPF</label>
        <InputText :model-value="store.company?.document" class="w-full" disabled />
        <p class="text-xs text-text-secondary">
          O documento não pode ser alterado por aqui. Fale com o suporte se precisar corrigi-lo.
        </p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="company-email" class="text-sm font-medium text-text-primary dark:text-white">
            E-mail de Contato
          </label>
          <InputText id="company-email" v-model="form.email" type="email" class="w-full" />
        </div>
        <div class="space-y-1">
          <label for="company-phone" class="text-sm font-medium text-text-primary dark:text-white">
            Telefone
          </label>
          <InputText id="company-phone" v-model="form.phone" class="w-full" />
        </div>
      </div>

      <Button
        type="submit"
        label="Salvar alterações"
        :loading="isSaving"
        data-testid="company-form-submit"
      />
    </form>
  </div>
</template>
