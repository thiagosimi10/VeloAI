<script setup lang="ts">
import { Moon, Sparkles, Sun, UserPlus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

function goToLogin(): void {
  router.push({ name: 'login' })
}

function goToDashboard(): void {
  router.push({ name: 'dashboard' })
}

function goToSignup(): void {
  router.push({ name: 'signup' })
}
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-black/5 bg-surface-light/80 backdrop-blur dark:border-white/10 dark:bg-surface-dark/80"
  >
    <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
      <router-link :to="{ name: 'landing' }" class="flex items-center gap-2">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-primary-active text-white"
        >
          <Sparkles :size="18" />
        </div>
        <span class="text-lg font-bold text-text-primary dark:text-white">VeloAI</span>
      </router-link>

      <nav class="hidden items-center gap-6 text-sm font-medium text-text-secondary md:flex">
        <a href="/#recursos" class="transition-colors hover:text-primary">Recursos</a>
        <a href="/#precos" class="transition-colors hover:text-primary">Preços</a>
        <a href="/#faq" class="transition-colors hover:text-primary">Perguntas Frequentes</a>
      </nav>

      <div class="flex items-center gap-2">
        <button
          type="button"
          aria-label="Alternar tema"
          class="rounded-md p-2 text-text-secondary transition-colors hover:bg-black/5 dark:hover:bg-white/10"
          @click="themeStore.toggle()"
        >
          <Moon v-if="themeStore.mode === 'light'" :size="18" />
          <Sun v-else :size="18" />
        </button>
        <button
          v-if="authStore.isAuthenticated"
          type="button"
          class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
          @click="goToDashboard"
        >
          Ir para o Painel
        </button>
        <template v-else>
          <button
            type="button"
            class="rounded-md px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-primary"
            @click="goToLogin"
          >
            Entrar
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover sm:px-4"
            @click="goToSignup"
          >
            <UserPlus :size="16" class="hidden sm:inline" />
            Cadastre-se
          </button>
        </template>
      </div>
    </div>
  </header>
</template>
