<script setup lang="ts">
import { ShieldCheck } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

import { useAdminAuthStore } from '@/stores/adminAuth'

const adminAuthStore = useAdminAuthStore()
const router = useRouter()

const form = reactive({
  email: '',
  password: '',
})

async function handleSubmit(): Promise<void> {
  const success = await adminAuthStore.login({ email: form.email, password: form.password })
  if (success) {
    await router.push({ name: 'admin-tenants' })
  }
}
</script>

<template>
  <form class="space-y-5" @submit.prevent="handleSubmit">
    <div class="flex flex-col items-center text-center">
      <div class="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-primary/10 text-primary">
        <ShieldCheck :size="22" />
      </div>
      <h1 class="text-xl font-semibold text-text-primary dark:text-white">
        Painel Administrativo
      </h1>
      <p class="mt-1 text-sm text-text-secondary">Acesso exclusivo da equipe VeloAI.</p>
    </div>

    <Message v-if="adminAuthStore.error" severity="error" :closable="false">
      {{ adminAuthStore.error }}
    </Message>

    <div class="space-y-1">
      <label for="admin-email" class="text-sm font-medium text-text-primary dark:text-white">
        E-mail
      </label>
      <InputText
        id="admin-email"
        v-model="form.email"
        type="email"
        autocomplete="email"
        required
        class="w-full"
        placeholder="operador@veloai.internal"
      />
    </div>

    <div class="space-y-1">
      <label for="admin-password" class="text-sm font-medium text-text-primary dark:text-white">
        Senha
      </label>
      <Password
        id="admin-password"
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
      :loading="adminAuthStore.isLoading"
      data-testid="admin-login-submit"
    />
  </form>
</template>
