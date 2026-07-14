<script setup lang="ts">
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  password: '',
})

async function handleSubmit(): Promise<void> {
  const success = await authStore.login({ email: form.email, password: form.password })
  if (success) {
    const redirect = (route.query.redirect as string) || '/dashboard'
    await router.push(redirect)
  }
}
</script>

<template>
  <form class="space-y-5" @submit.prevent="handleSubmit">
    <div>
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">Entrar no VeloAI</h1>
      <p class="mt-1 text-sm text-text-secondary">Acesse sua conta para continuar.</p>
    </div>

    <Message v-if="authStore.error" severity="error" :closable="false">
      {{ authStore.error }}
    </Message>

    <div class="space-y-1">
      <label for="email" class="text-sm font-medium text-text-primary dark:text-white">
        E-mail
      </label>
      <InputText
        id="email"
        v-model="form.email"
        type="email"
        autocomplete="email"
        required
        class="w-full"
        placeholder="voce@empresa.com"
      />
    </div>

    <div class="space-y-1">
      <label for="password" class="text-sm font-medium text-text-primary dark:text-white">
        Senha
      </label>
      <Password
        id="password"
        v-model="form.password"
        :feedback="false"
        toggle-mask
        input-class="w-full"
        class="w-full"
        autocomplete="current-password"
        required
      />
    </div>

    <Button
      type="submit"
      label="Entrar"
      class="w-full"
      :loading="authStore.isLoading"
      data-testid="login-submit"
    />
  </form>
</template>
