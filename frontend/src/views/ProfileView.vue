<script setup lang="ts">
import { KeyRound, Upload, User } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useToast } from 'primevue/usetoast'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const form = reactive({
  firstName: authStore.user?.firstName ?? '',
  lastName: authStore.user?.lastName ?? '',
})

const isSavingProfile = ref(false)
const isUploadingAvatar = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const avatarError = ref<string | null>(null)

const userInitial = computed(() => authStore.user?.firstName.charAt(0).toUpperCase() ?? '?')

function triggerFileSelect(): void {
  fileInput.value?.click()
}

async function handleFileChange(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  avatarError.value = null
  isUploadingAvatar.value = true
  const success = await authStore.uploadAvatar(file)
  isUploadingAvatar.value = false
  input.value = ''

  if (success) {
    toast.add({ severity: 'success', summary: 'Foto atualizada', life: 3000 })
  } else {
    avatarError.value = authStore.error
  }
}

async function handleSubmit(): Promise<void> {
  isSavingProfile.value = true
  const success = await authStore.updateProfile({
    firstName: form.firstName,
    lastName: form.lastName || null,
  })
  isSavingProfile.value = false

  if (success) {
    toast.add({ severity: 'success', summary: 'Perfil atualizado', life: 3000 })
  }
}

function goToChangePassword(): void {
  router.push({ name: 'change-password' })
}
</script>

<template>
  <div class="max-w-2xl space-y-5">
    <h1 class="text-xl font-semibold text-text-primary dark:text-white">Meu Perfil</h1>

    <Message v-if="authStore.error" severity="error" :closable="false">{{ authStore.error }}</Message>

    <div
      class="rounded-xl border border-black/5 bg-surface-light p-5 shadow-sm dark:border-white/10 dark:bg-surface-dark"
    >
      <div class="flex items-center gap-4">
        <div class="relative">
          <img
            v-if="authStore.user?.avatarUrl"
            :src="authStore.user.avatarUrl"
            alt="Foto de perfil"
            class="h-20 w-20 rounded-full object-cover"
          />
          <div
            v-else
            class="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-2xl font-semibold text-primary"
          >
            {{ userInitial }}
          </div>
        </div>
        <div>
          <button
            type="button"
            data-testid="upload-avatar-button"
            class="flex items-center gap-2 rounded-md border border-black/10 px-3 py-1.5 text-sm font-medium text-text-primary hover:bg-black/5 dark:border-white/10 dark:text-white dark:hover:bg-white/10"
            :disabled="isUploadingAvatar"
            @click="triggerFileSelect"
          >
            <Upload :size="16" />
            {{ isUploadingAvatar ? 'Enviando...' : 'Alterar foto' }}
          </button>
          <p class="mt-1 text-xs text-text-secondary">JPEG, PNG ou WEBP, até 2MB.</p>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
            @change="handleFileChange"
          />
        </div>
      </div>
      <Message v-if="avatarError" severity="error" :closable="false" class="mt-3">
        {{ avatarError }}
      </Message>
    </div>

    <form
      class="space-y-4 rounded-xl border border-black/5 bg-surface-light p-5 shadow-sm dark:border-white/10 dark:bg-surface-dark"
      @submit.prevent="handleSubmit"
    >
      <div class="flex items-center gap-2">
        <User :size="18" class="text-text-secondary" />
        <h2 class="text-sm font-semibold text-text-primary dark:text-white">Dados pessoais</h2>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1">
          <label for="profile-first-name" class="text-sm font-medium text-text-primary dark:text-white">
            Nome
          </label>
          <InputText id="profile-first-name" v-model="form.firstName" class="w-full" required />
        </div>
        <div class="space-y-1">
          <label for="profile-last-name" class="text-sm font-medium text-text-primary dark:text-white">
            Sobrenome
          </label>
          <InputText id="profile-last-name" v-model="form.lastName" class="w-full" />
        </div>
      </div>

      <div class="space-y-1">
        <label class="text-sm font-medium text-text-primary dark:text-white">E-mail</label>
        <InputText :model-value="authStore.user?.email" class="w-full" disabled />
      </div>

      <Button
        type="submit"
        label="Salvar alterações"
        :loading="isSavingProfile"
        data-testid="profile-form-submit"
      />
    </form>

    <div
      class="flex items-center justify-between rounded-xl border border-black/5 bg-surface-light p-5 shadow-sm dark:border-white/10 dark:bg-surface-dark"
    >
      <div class="flex items-center gap-2">
        <KeyRound :size="18" class="text-text-secondary" />
        <div>
          <p class="text-sm font-medium text-text-primary dark:text-white">Senha</p>
          <p class="text-xs text-text-secondary">Altere sua senha de acesso a qualquer momento.</p>
        </div>
      </div>
      <Button label="Alterar senha" severity="secondary" @click="goToChangePassword" />
    </div>
  </div>
</template>
