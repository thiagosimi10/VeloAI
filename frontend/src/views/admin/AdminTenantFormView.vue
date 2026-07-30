<script setup lang="ts">
import { ArrowLeft, Building2, Check, Copy, KeyRound } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { type TenantProvisioned, useAdminStore } from '@/stores/admin'
import { formatDocumentInput } from '@/utils/mask'

const store = useAdminStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const tenantId = computed(() => (typeof route.params.id === 'string' ? route.params.id : null))
const isEditing = computed(() => tenantId.value !== null)
const isLoading = ref(false)
const provisioned = ref<TenantProvisioned | null>(null)
const copied = ref(false)

const form = reactive({
  legalName: '',
  tradeName: '',
  document: '',
  adminName: '',
  adminEmail: '',
})

const documentDisplay = computed({
  get: () => form.document,
  set: (value: string) => {
    form.document = formatDocumentInput(value)
  },
})

onMounted(async () => {
  if (!tenantId.value) {
    return
  }

  if (store.tenants.length === 0) {
    await store.fetchTenants()
  }

  const tenant = store.tenants.find((item) => item.tenantId === tenantId.value)
  if (tenant) {
    form.legalName = tenant.legalName
    form.tradeName = tenant.tradeName ?? ''
  }
})

async function handleSubmit(): Promise<void> {
  isLoading.value = true

  if (isEditing.value && tenantId.value) {
    const success = await store.updateTenant(tenantId.value, {
      legalName: form.legalName,
      tradeName: form.tradeName || null,
    })
    isLoading.value = false
    if (success) {
      toast.add({ severity: 'success', summary: 'Empresa atualizada', life: 3000 })
      await router.push({ name: 'admin-tenants' })
    }
    return
  }

  const result = await store.createTenant({
    legalName: form.legalName,
    tradeName: form.tradeName || null,
    document: form.document,
    adminName: form.adminName,
    adminEmail: form.adminEmail,
  })
  isLoading.value = false
  if (result) {
    provisioned.value = result
  }
}

async function copyPassword(): Promise<void> {
  if (!provisioned.value) {
    return
  }
  await navigator.clipboard.writeText(provisioned.value.admin.temporaryPassword)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-5">
    <button
      type="button"
      class="group flex items-center gap-1.5 text-sm text-text-secondary transition-colors hover:text-primary"
      @click="router.push({ name: 'admin-tenants' })"
    >
      <ArrowLeft :size="14" class="transition-transform group-hover:-translate-x-0.5" />
      Voltar para Empresas
    </button>

    <div class="flex items-center gap-3">
      <div class="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
        <Building2 :size="20" />
      </div>
      <div>
        <h1 class="text-xl font-semibold text-text-primary dark:text-white">
          {{ isEditing ? 'Editar Empresa' : 'Nova Empresa' }}
        </h1>
        <p class="text-sm text-text-secondary">
          {{
            isEditing
              ? 'Atualize os dados cadastrais desta empresa.'
              : 'Provisiona um novo ambiente completo para a empresa.'
          }}
        </p>
      </div>
    </div>

    <Transition
      mode="out-in"
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
    >
    <div
      v-if="provisioned"
      class="space-y-4 rounded-lg border border-success/20 bg-success/5 p-6 shadow-sm"
    >
      <div class="flex items-center gap-2 text-success">
        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-success/15">
          <Check :size="16" />
        </div>
        <p class="font-medium">Empresa "{{ provisioned.legalName }}" criada com sucesso.</p>
      </div>

      <p class="text-sm text-text-secondary">
        Repasse estas credenciais ao responsável pela empresa — ainda não há envio automático
        de e-mail. A senha é temporária e será exigida a troca no primeiro login.
      </p>

      <div class="space-y-3 rounded-md border border-black/5 bg-surface-light p-4 dark:border-white/10 dark:bg-surface-dark">
        <div>
          <p class="text-xs text-text-secondary">E-mail</p>
          <p class="font-medium text-text-primary dark:text-white">
            {{ provisioned.admin.adminEmail }}
          </p>
        </div>
        <div>
          <p class="text-xs text-text-secondary">Senha temporária</p>
          <div class="flex items-center gap-2">
            <code
              class="flex-1 rounded-md bg-black/5 px-3 py-1.5 font-mono text-sm text-text-primary dark:bg-white/10 dark:text-white"
            >{{ provisioned.admin.temporaryPassword }}</code>
            <button
              type="button"
              class="flex items-center gap-1 rounded-md px-2 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/10"
              @click="copyPassword"
            >
              <Check v-if="copied" :size="14" class="text-success" />
              <Copy v-else :size="14" />
              {{ copied ? 'Copiado!' : 'Copiar' }}
            </button>
          </div>
        </div>
      </div>

      <Button label="Voltar para Empresas" @click="router.push({ name: 'admin-tenants' })" />
    </div>

    <form
      v-else
      class="space-y-6 rounded-lg border border-black/5 bg-surface-light p-6 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      @submit.prevent="handleSubmit"
    >
      <Message v-if="store.error" severity="error" :closable="false">{{ store.error }}</Message>

      <div class="space-y-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-text-secondary">
          Dados da Empresa
        </p>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label
              for="tenant-legal-name"
              class="text-sm font-medium text-text-primary dark:text-white"
            >
              Razão Social
            </label>
            <InputText id="tenant-legal-name" v-model="form.legalName" class="w-full" required />
          </div>
          <div class="space-y-1">
            <label
              for="tenant-trade-name"
              class="text-sm font-medium text-text-primary dark:text-white"
            >
              Nome Fantasia
            </label>
            <InputText id="tenant-trade-name" v-model="form.tradeName" class="w-full" />
          </div>
        </div>

        <div v-if="!isEditing" class="space-y-1">
          <label for="tenant-document" class="text-sm font-medium text-text-primary dark:text-white">
            CNPJ
          </label>
          <InputText
            id="tenant-document"
            v-model="documentDisplay"
            class="w-full"
            placeholder="00.000.000/0000-00"
            required
          />
        </div>
      </div>

      <template v-if="!isEditing">
        <div class="h-px bg-black/5 dark:bg-white/10" />

        <div class="space-y-4">
          <p class="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-secondary">
            <KeyRound :size="12" />
            Responsável pela Empresa
          </p>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label
                for="tenant-admin-name"
                class="text-sm font-medium text-text-primary dark:text-white"
              >
                Nome
              </label>
              <InputText id="tenant-admin-name" v-model="form.adminName" class="w-full" required />
            </div>
            <div class="space-y-1">
              <label
                for="tenant-admin-email"
                class="text-sm font-medium text-text-primary dark:text-white"
              >
                E-mail
              </label>
              <InputText
                id="tenant-admin-email"
                v-model="form.adminEmail"
                type="email"
                class="w-full"
                required
              />
            </div>
          </div>
          <p class="text-xs text-text-secondary">
            Uma senha temporária será gerada automaticamente para este usuário.
          </p>
        </div>
      </template>

      <div class="flex gap-2 pt-2">
        <Button
          type="submit"
          label="Salvar"
          :loading="isLoading"
          data-testid="tenant-form-submit"
        />
        <Button
          type="button"
          label="Cancelar"
          severity="secondary"
          @click="router.push({ name: 'admin-tenants' })"
        />
      </div>
    </form>
    </Transition>
  </div>
</template>
