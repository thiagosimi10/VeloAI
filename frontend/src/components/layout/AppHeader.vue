<script setup lang="ts">
import { Building2, LogOut, Moon, Search, Sparkles, Sun, UserCircle } from 'lucide-vue-next'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAiStore } from '@/stores/ai'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

import CommandPalette from './CommandPalette.vue'

const themeStore = useThemeStore()
const authStore = useAuthStore()
const aiStore = useAiStore()
const router = useRouter()

const isUserMenuOpen = ref(false)
const isPaletteOpen = ref(false)

function handleGlobalKeydown(event: KeyboardEvent): void {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    isPaletteOpen.value = true
  }
}

onMounted(() => {
  themeStore.initialize()
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

const userInitial = computed(() => authStore.user?.firstName.charAt(0).toUpperCase() ?? '?')

function goToProfile(): void {
  isUserMenuOpen.value = false
  router.push({ name: 'profile' })
}

function goToCompanySettings(): void {
  isUserMenuOpen.value = false
  router.push({ name: 'company-settings' })
}

async function handleLogout(): Promise<void> {
  isUserMenuOpen.value = false
  await authStore.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <header
    class="flex h-16 items-center justify-between border-b border-black/5 bg-surface-light px-6 dark:border-white/10 dark:bg-surface-dark"
  >
    <button
      type="button"
      class="flex items-center gap-2 rounded-md border border-black/10 px-3 py-1.5 text-sm text-text-secondary hover:bg-black/5 dark:border-white/10 dark:hover:bg-white/10"
      @click="isPaletteOpen = true"
    >
      <Search :size="16" />
      <span>Ir para...</span>
      <kbd class="ml-4 rounded bg-black/5 px-1.5 py-0.5 text-xs dark:bg-white/10">Ctrl K</kbd>
    </button>

    <CommandPalette v-if="isPaletteOpen" @close="isPaletteOpen = false" />

    <div class="flex items-center gap-2">
      <button
        type="button"
        data-testid="ask-ai-button"
        class="flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-hover"
        @click="aiStore.toggleChat()"
      >
        <Sparkles :size="16" />
        <span>Perguntar para IA</span>
      </button>

      <button
        type="button"
        :aria-label="themeStore.mode === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'"
        class="rounded-md p-2 text-text-secondary hover:bg-black/5 dark:hover:bg-white/10"
        @click="themeStore.toggle()"
      >
        <Sun v-if="themeStore.mode === 'dark'" :size="20" />
        <Moon v-else :size="20" />
      </button>

      <div class="relative">
        <button
          type="button"
          aria-label="Menu do usuário"
          data-testid="user-menu-button"
          class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-primary/10 text-sm font-semibold text-primary"
          @click="isUserMenuOpen = !isUserMenuOpen"
        >
          <img
            v-if="authStore.user?.avatarUrl"
            :src="authStore.user.avatarUrl"
            alt="Foto de perfil"
            class="h-full w-full object-cover"
          />
          <span v-else>{{ userInitial }}</span>
        </button>

        <div
          v-if="isUserMenuOpen"
          class="absolute right-0 top-11 z-10 w-60 rounded-md border border-black/10 bg-surface-light p-2 shadow-lg dark:border-white/10 dark:bg-surface-dark"
        >
          <div class="px-2 py-1.5">
            <p class="truncate text-sm font-medium text-text-primary dark:text-white">
              {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
            </p>
            <p class="truncate text-xs text-text-secondary">{{ authStore.user?.email }}</p>
          </div>
          <hr class="my-1 border-black/10 dark:border-white/10" />
          <button
            type="button"
            data-testid="my-profile-button"
            class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-text-primary hover:bg-black/5 dark:text-white dark:hover:bg-white/10"
            @click="goToProfile"
          >
            <UserCircle :size="16" />
            Meu Perfil
          </button>
          <button
            v-if="authStore.hasPermission('system.admin')"
            type="button"
            data-testid="company-settings-button"
            class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-text-primary hover:bg-black/5 dark:text-white dark:hover:bg-white/10"
            @click="goToCompanySettings"
          >
            <Building2 :size="16" />
            Configurações da Empresa
          </button>
          <hr class="my-1 border-black/10 dark:border-white/10" />
          <button
            type="button"
            data-testid="logout-button"
            class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm text-text-primary hover:bg-black/5 dark:text-white dark:hover:bg-white/10"
            @click="handleLogout"
          >
            <LogOut :size="16" />
            Sair
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
