<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { computed, reactive } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const mismatchError = computed(() =>
  form.confirmPassword.length > 0 && form.newPassword !== form.confirmPassword
    ? 'As senhas não coincidem.'
    : null,
)

async function handleSubmit(): Promise<void> {
  if (mismatchError.value) {
    return
  }

  const success = await authStore.changePassword({
    currentPassword: form.currentPassword,
    newPassword: form.newPassword,
  })

  if (success) {
    await router.push({ name: 'dashboard' })
  }
}
</script>

<template>
  <form class="space-y-5" @submit.prevent="handleSubmit">
    <div>
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">
        Defina uma nova senha
      </h1>
      <p class="mt-1 text-sm text-text-secondary">
        Por segurança, você precisa trocar a senha temporária antes de continuar.
      </p>
    </div>

    <Message v-if="authStore.error" severity="error" :closable="false">
      {{ authStore.error }}
    </Message>
    <Message v-if="mismatchError" severity="warn" :closable="false">
      {{ mismatchError }}
    </Message>

    <div class="space-y-1">
      <label for="current-password" class="text-sm font-medium text-text-primary dark:text-white">
        Senha atual
      </label>
      <Password
        id="current-password"
        v-model="form.currentPassword"
        :feedback="false"
        toggle-mask
        input-class="w-full"
        class="w-full"
        autocomplete="current-password"
        required
      />
    </div>

    <div class="space-y-1">
      <label for="new-password" class="text-sm font-medium text-text-primary dark:text-white">
        Nova senha
      </label>
      <Password
        id="new-password"
        v-model="form.newPassword"
        toggle-mask
        input-class="w-full"
        class="w-full"
        autocomplete="new-password"
        required
      />
    </div>

    <div class="space-y-1">
      <label for="confirm-password" class="text-sm font-medium text-text-primary dark:text-white">
        Confirme a nova senha
      </label>
      <Password
        id="confirm-password"
        v-model="form.confirmPassword"
        :feedback="false"
        toggle-mask
        input-class="w-full"
        class="w-full"
        autocomplete="new-password"
        required
      />
    </div>

    <Button
      type="submit"
      label="Salvar nova senha"
      class="w-full"
      :loading="authStore.isLoading"
      :disabled="Boolean(mismatchError)"
      data-testid="change-password-submit"
    />
  </form>
</template>
